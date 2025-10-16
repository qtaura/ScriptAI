"""
    Monitoring and logging utilities for ScriptAI
Tracks usage, errors, and performance metrics, and exposes Prometheus metrics.
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
import logging
import logging.config
from logging import LogRecord


# Optional TRACE level support for very verbose logging
TRACE_LEVEL_NUM = 5
if not hasattr(logging, "TRACE"):
    logging.TRACE = TRACE_LEVEL_NUM  # type: ignore[attr-defined]
    logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logs suitable for production."""

    def format(self, record: LogRecord) -> str:
        try:
            ts = datetime.utcfromtimestamp(record.created).isoformat() + "Z"
        except Exception:
            ts = datetime.utcnow().isoformat() + "Z"

        log: Dict[str, Any] = {
            "timestamp": ts,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Optional extra fields commonly used in our app
        # Use getattr to avoid AttributeError if missing
        req_id = getattr(record, "request_id", None)
        model_name = getattr(record, "model_name", None)
        client_ip = getattr(record, "client_ip", None)
        endpoint = getattr(record, "endpoint", None)
        method = getattr(record, "method", None)
        status = getattr(record, "status", None)
        error = getattr(record, "error", None)
        response_time = getattr(record, "response_time", None)
        prompt_length = getattr(record, "prompt_length", None)
        success = getattr(record, "success", None)

        if req_id is not None:
            log["request_id"] = req_id
        if model_name is not None:
            log["model_name"] = model_name
        if client_ip is not None:
            log["client_ip"] = client_ip
        if endpoint is not None:
            log["endpoint"] = endpoint
        if method is not None:
            log["method"] = method
        if status is not None:
            log["status"] = status
        if error is not None:
            log["error"] = error
        if response_time is not None:
            log["response_time"] = response_time
        if prompt_length is not None:
            log["prompt_length"] = prompt_length
        if success is not None:
            log["success"] = success

        return json.dumps(log, ensure_ascii=False)


def _get_prom_client() -> Optional[Any]:
    """Return prometheus_client module if available, else None."""
    try:
        import prometheus_client as prom_mod

        return prom_mod
    except ImportError:  # pragma: no cover
        return None


class MonitoringManager:
    """Manages monitoring, logging, and analytics for ScriptAI"""

    # Prometheus metrics (initialized when client is available)
    request_counter: Optional[Any]
    request_latency: Optional[Any]
    error_counter: Optional[Any]

    def __init__(
        self,
        log_file: str = "scriptai.log",
        max_log_size: int = 10 * 1024 * 1024,
        enable_metrics: bool = True,
    ):
        self.log_file = log_file
        self.max_log_size = max_log_size
        self.usage_stats: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.performance_metrics: deque = deque(maxlen=1000)  # Keep last 1000 requests

        # Global data privacy mode: when enabled, disable disk persistence
        try:
            _pm = os.getenv("DATA_PRIVACY_MODE", "false").strip().lower()
            self.privacy_mode = _pm in {"1", "true", "yes", "on"}
        except Exception:
            self.privacy_mode = False

        # Setup logging
        self.setup_logging()

        # Load existing stats if available
        if not self.privacy_mode:
            self.load_stats()

        # Initialize Prometheus metrics if available
        # Initialize Prometheus metrics unless disabled
        if enable_metrics:
            self._init_prometheus_metrics()

        # Ensure attributes exist for type checkers even if init path changes
        if not hasattr(self, "request_counter"):
            self.request_counter = None
        if not hasattr(self, "request_latency"):
            self.request_latency = None
        if not hasattr(self, "error_counter"):
            self.error_counter = None

    def setup_logging(self):
        """Setup logging configuration.

        Tries centralized config via LOGGING_CONFIG env var or default files:
        logging.yaml / logging.yml / logging.json. Falls back to JSONFormatter
        with console and optional file handlers when no config is found or fails.
        """

        applied_config = False

        # Environment-driven settings
        level_name = os.getenv("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, level_name, logging.INFO)

        def _env_bool(name: str, default: bool = True) -> bool:
            raw = os.getenv(name)
            if raw is None:
                return default
            val = raw.strip().lower()
            if val in {"0", "false", "no", "off"}:
                return False
            if val in {"1", "true", "yes", "on"}:
                return True
            return default

        log_to_file = _env_bool("LOG_TO_FILE", True)
        # Override via privacy mode: disable file logging entirely
        try:
            _pm = os.getenv("DATA_PRIVACY_MODE", "false").strip().lower()
            if _pm in {"1", "true", "yes", "on"}:
                log_to_file = False
        except Exception:
            pass
        env_log_file = os.getenv("LOG_FILE_PATH", self.log_file)

        # Detect serverless environments (e.g., Vercel/AWS Lambda) and avoid file logging
        def _is_serverless_env() -> bool:
            try:
                return any(
                    os.getenv(name)
                    for name in (
                        "VERCEL",
                        "VERCEL_REGION",
                        "AWS_LAMBDA_FUNCTION_NAME",
                        "LAMBDA_TASK_ROOT",
                    )
                )
            except Exception:
                return False

        is_serverless = _is_serverless_env()
        if is_serverless:
            # File system under /var/task is read-only; prefer console logging
            log_to_file = False
            # If needed elsewhere, normalize to /tmp for any incidental file ops
            try:
                env_log_file = os.path.join("/tmp", os.path.basename(env_log_file))
            except Exception:
                # Fallback silently if path ops fail
                pass

        # Final guard: disable file logging if target directory is not writable
        def _dir_is_writable(path: str) -> bool:
            try:
                directory = os.path.dirname(path) or "."
                return os.path.isdir(directory) and os.access(directory, os.W_OK)
            except Exception:
                return False

        if log_to_file and not _dir_is_writable(env_log_file):
            log_to_file = False

        # Candidate config paths
        candidates: List[str] = []
        env_path = os.getenv("LOGGING_CONFIG")
        if env_path and env_path.strip():
            candidates.append(env_path.strip())
        candidates.extend(["logging.yaml", "logging.yml", "logging.json"])

        for path in candidates:
            try:
                if not os.path.exists(path):
                    continue

                config_data: Optional[Dict[str, Any]] = None
                if path.endswith((".yaml", ".yml")):
                    try:
                        import yaml  # type: ignore

                        with open(path, "r", encoding="utf-8") as f:
                            config_data = yaml.safe_load(f)
                    except Exception:
                        # YAML not available or failed to parse; continue
                        config_data = None
                elif path.endswith(".json"):
                    with open(path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)

                if isinstance(config_data, dict):
                    # Apply environment overrides for level and file logging
                    try:
                        # Root level
                        root_cfg = config_data.setdefault("root", {})
                        root_cfg["level"] = level_name

                        # Handlers adjustments
                        handlers = config_data.setdefault("handlers", {})
                        # Update file handler path if present
                        if "file" in handlers:
                            handlers["file"]["filename"] = env_log_file
                            # Disable file handler entirely if LOG_TO_FILE=false
                            if not log_to_file:
                                handlers.pop("file", None)
                                # Remove file from root handlers list
                                root_handlers = root_cfg.setdefault("handlers", [])
                                root_cfg["handlers"] = [
                                    h for h in root_handlers if h != "file"
                                ]

                        # Ensure console exists
                        if "console" in handlers:
                            handlers["console"]["level"] = level_name

                        # Update explicit logger levels (optional)
                        loggers_cfg = config_data.setdefault("loggers", {})
                        for name, lc in loggers_cfg.items():
                            try:
                                if isinstance(lc, dict):
                                    lc["level"] = level_name
                                    # Also remove file handler from individual loggers when disabled
                                    if not log_to_file and "handlers" in lc:
                                        lc["handlers"] = [
                                            h
                                            for h in lc.get("handlers", [])
                                            if h != "file"
                                        ]
                            except Exception:
                                # Ignore malformed logger config
                                pass
                    except Exception:
                        # Ignore overrides if anything goes wrong
                        pass

                    try:
                        logging.config.dictConfig(config_data)
                        # Ensure the configured level is applied to the root
                        logging.getLogger().setLevel(log_level)
                        applied_config = True
                        break
                    except Exception:
                        # DictConfig failed; try next candidate
                        applied_config = False
                        continue
            except Exception:
                # Never crash due to logging config
                applied_config = False
                continue

        if not applied_config:
            # Fallback: configure handlers explicitly for consistent JSON output
            stream_handler = logging.StreamHandler()
            formatter = JSONFormatter()
            stream_handler.setFormatter(formatter)

            root = logging.getLogger()
            root.handlers = []
            root.setLevel(log_level)
            root.addHandler(stream_handler)
            if log_to_file:
                try:
                    file_handler = logging.FileHandler(env_log_file)
                    file_handler.setFormatter(formatter)
                    root.addHandler(file_handler)
                except Exception:
                    # If file handler fails (e.g., read-only FS), continue with console only
                    pass

        self.logger = logging.getLogger("ScriptAI")

    def _init_prometheus_metrics(self):
        """Initialize Prometheus counters and histograms if the client is installed."""
        prom = _get_prom_client()
        if prom is None:
            # Prometheus client not installed; skip initialization
            self.request_counter = None
            self.request_latency = None
            self.error_counter = None
            return

        # Total requests by endpoint/method/status
        self.request_counter = prom.Counter(
            "scriptai_requests_total",
            "Total HTTP requests",
            ["endpoint", "method", "status"],
        )

        # Request latency histogram
        self.request_latency = prom.Histogram(
            "scriptai_request_duration_seconds",
            "HTTP request latency in seconds",
            ["endpoint", "method", "status"],
        )

        # Error counter by type
        self.error_counter = prom.Counter(
            "scriptai_errors_total",
            "Total errors",
            ["error_type"],
        )

    def log_request(
        self,
        model: str,
        prompt_length: int,
        response_time: float,
        success: bool,
        client_ip: Optional[str] = None,
        error: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        """
        Log a request with metrics

        Args:
            model: AI model used
            prompt_length: Length of input prompt
            response_time: Time taken to generate response
            success: Whether request was successful
            client_ip: Client IP address
            error: Error message if any
        """
        timestamp = datetime.now()

        # Update usage stats
        self.usage_stats["total_requests"] += 1
        self.usage_stats[f"model_{model}_requests"] += 1
        self.usage_stats["total_prompt_chars"] += prompt_length

        if success:
            self.usage_stats["successful_requests"] += 1
        else:
            self.usage_stats["failed_requests"] += 1
            if error:
                self.error_counts[error] += 1

        # Store performance metrics
        metric = {
            "timestamp": timestamp.isoformat(),
            "model": model,
            "prompt_length": prompt_length,
            "response_time": response_time,
            "success": success,
            "client_ip": client_ip,
            "error": error,
        }
        self.performance_metrics.append(metric)

        # Log structured event
        log_level = logging.INFO if success else logging.ERROR
        extra = {
            "request_id": request_id,
            "model_name": model,
            "client_ip": client_ip,
            "response_time": round(response_time, 4),
            "prompt_length": prompt_length,
            "success": success,
            "error": error,
        }
        self.logger.log(log_level, "model_generate", extra=extra)

        # Prometheus metrics
        try:
            if self.request_counter and self.request_latency:
                status_label = "success" if success else "error"
                # Use model as endpoint label when route context is not available
                self.request_counter.labels(
                    endpoint=model, method="POST", status=status_label
                ).inc()
                self.request_latency.labels(
                    endpoint=model, method="POST", status=status_label
                ).observe(response_time)
        except Exception:
            # Never let metrics raise
            pass

        # Save stats periodically
        if self.usage_stats["total_requests"] % 10 == 0:
            self.save_stats()

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """
        Log an error with context

        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context
        """
        self.error_counts[error_type] += 1

        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {},
        }

        self.logger.error(
            f"{error_type}: {error_message}",
            extra={
                "request_id": request_id,
                "error": error_message,
                "context": context or {},
            },
        )

        # Prometheus error counter
        try:
            if self.error_counter:
                self.error_counter.labels(error_type=error_type).inc()
        except Exception:
            pass

    def get_usage_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get usage statistics for the last N hours

        Args:
            hours: Number of hours to look back

        Returns:
            Dictionary with usage statistics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter metrics by time
        recent_metrics = [
            m
            for m in self.performance_metrics
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]

        if not recent_metrics:
            return {
                "total_requests": 0,
                "success_rate": 0,
                "avg_response_time": 0,
                "models_used": {},
                "errors": {},
            }

        # Calculate statistics
        total_requests = len(recent_metrics)
        successful_requests = sum(1 for m in recent_metrics if m["success"])
        success_rate = (
            (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        )

        avg_response_time = (
            sum(m["response_time"] for m in recent_metrics) / total_requests
        )

        # Model usage
        models_used: Dict[str, int] = defaultdict(int)
        for metric in recent_metrics:
            models_used[metric["model"]] += 1

        # Error counts
        errors: Dict[str, int] = defaultdict(int)
        for metric in recent_metrics:
            if not metric["success"] and metric["error"]:
                errors[metric["error"]] += 1

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": round(success_rate, 2),
            "avg_response_time": round(avg_response_time, 2),
            "models_used": dict(models_used),
            "errors": dict(errors),
            "time_period_hours": hours,
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics

        Returns:
            Dictionary with performance data
        """
        if not self.performance_metrics:
            return {"message": "No performance data available"}

        response_times = [m["response_time"] for m in self.performance_metrics]
        sorted_times = sorted(response_times)

        def percentile(values, p):
            if not values:
                return 0.0
            if p <= 0:
                return float(values[0])
            if p >= 100:
                return float(values[-1])
            k = (len(values) - 1) * (p / 100.0)
            f = int(k)
            c = min(f + 1, len(values) - 1)
            if f == c:
                return float(values[int(k)])
            d0 = values[f] * (c - k)
            d1 = values[c] * (k - f)
            return float(d0 + d1)

        return {
            "avg_response_time": round(sum(response_times) / len(response_times), 2),
            "min_response_time": round(min(response_times), 2),
            "max_response_time": round(max(response_times), 2),
            "p50_response_time": round(percentile(sorted_times, 50), 2),
            "p95_response_time": round(percentile(sorted_times, 95), 2),
            "p99_response_time": round(percentile(sorted_times, 99), 2),
            "total_requests": len(self.performance_metrics),
            "success_rate": round(
                sum(1 for m in self.performance_metrics if m["success"])
                / len(self.performance_metrics)
                * 100,
                2,
            ),
        }

    def check_health(self) -> Dict[str, Any]:
        """
        Check system health

        Returns:
            Dictionary with health status
        """
        # Check log file size
        log_size = 0
        if os.path.exists(self.log_file):
            log_size = os.path.getsize(self.log_file)

        # Check recent error rate
        recent_stats = self.get_usage_stats(hours=1)
        error_rate = 100 - recent_stats.get("success_rate", 100)

        # Determine health status
        if error_rate > 50:
            health_status = "critical"
        elif error_rate > 20:
            health_status = "warning"
        else:
            health_status = "healthy"

        return {
            "status": health_status,
            "error_rate": error_rate,
            "log_size_mb": round(log_size / (1024 * 1024), 2),
            "total_requests": self.usage_stats["total_requests"],
            "uptime_hours": self.get_uptime_hours(),
        }

    def get_uptime_hours(self) -> float:
        """Get system uptime in hours"""
        # This is a simplified version - in production you'd track actual start time
        return 24.0  # Placeholder

    def save_stats(self):
        """Save statistics to file"""
        # Skip persistence in privacy mode
        if getattr(self, "privacy_mode", False):
            return
        stats_data = {
            "usage_stats": dict(self.usage_stats),
            "error_counts": dict(self.error_counts),
            "last_updated": datetime.now().isoformat(),
        }

        try:
            with open("scriptai_stats.json", "w") as f:
                json.dump(stats_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save stats: {e}")

    def load_stats(self):
        """Load statistics from file"""
        # Skip disk reads in privacy mode
        if getattr(self, "privacy_mode", False):
            return
        try:
            if os.path.exists("scriptai_stats.json"):
                with open("scriptai_stats.json", "r") as f:
                    stats_data = json.load(f)
                    self.usage_stats.update(stats_data.get("usage_stats", {}))
                    self.error_counts.update(stats_data.get("error_counts", {}))
        except Exception as e:
            self.logger.error(f"Failed to load stats: {e}")

    def cleanup_old_data(self, days: int = 30):
        """
        Clean up old performance metrics and logs

        Args:
            days: Number of days to keep
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        # Clean up old metrics
        self.performance_metrics = deque(
            [
                m
                for m in self.performance_metrics
                if datetime.fromisoformat(m["timestamp"]) > cutoff_time
            ],
            maxlen=1000,
        )

        # Rotate log file if too large
        if (
            os.path.exists(self.log_file)
            and os.path.getsize(self.log_file) > self.max_log_size
        ):
            backup_file = f"{self.log_file}.{int(time.time())}"
            os.rename(self.log_file, backup_file)
            self.logger.info(f"Log rotated to {backup_file}")

    def export_analytics(self, format: str = "json") -> str:
        """
        Export analytics data

        Args:
            format: Export format ('json' or 'csv')

        Returns:
            Exported data as string
        """
        if format == "json":
            return json.dumps(
                {
                    "usage_stats": dict(self.usage_stats),
                    "error_counts": dict(self.error_counts),
                    "performance_metrics": list(self.performance_metrics),
                    "exported_at": datetime.now().isoformat(),
                },
                indent=2,
            )

        elif format == "csv":
            # Simple CSV export of performance metrics
            csv_data = "timestamp,model,prompt_length,response_time,success,error\n"
            for metric in self.performance_metrics:
                csv_data += f"{metric['timestamp']},{metric['model']},{metric['prompt_length']},{metric['response_time']},{metric['success']},{metric.get('error', '')}\n"
            return csv_data

        return "Unsupported format"
