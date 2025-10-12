"""
Monitoring and logging utilities for ScriptAI
Tracks usage, errors, and performance metrics
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
import logging


class MonitoringManager:
    """Manages monitoring, logging, and analytics for ScriptAI"""

    def __init__(
        self, log_file: str = "scriptai.log", max_log_size: int = 10 * 1024 * 1024
    ):
        self.log_file = log_file
        self.max_log_size = max_log_size
        self.usage_stats: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.performance_metrics: deque = deque(maxlen=1000)  # Keep last 1000 requests

        # Setup logging
        self.setup_logging()

        # Load existing stats if available
        self.load_stats()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(self.log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger("ScriptAI")

    def log_request(
        self,
        model: str,
        prompt_length: int,
        response_time: float,
        success: bool,
        client_ip: Optional[str] = None,
        error: Optional[str] = None,
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

        # Log to file
        log_level = logging.INFO if success else logging.ERROR
        self.logger.log(
            log_level,
            f"Request: model={model}, time={response_time:.2f}s, success={success}",
        )

        if error:
            self.logger.error(f"Error: {error}")

        # Save stats periodically
        if self.usage_stats["total_requests"] % 10 == 0:
            self.save_stats()

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
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

        self.logger.error(f"Error: {error_type} - {error_message}")
        if context:
            self.logger.error(f"Context: {json.dumps(context)}")

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

        return {
            "avg_response_time": round(sum(response_times) / len(response_times), 2),
            "min_response_time": round(min(response_times), 2),
            "max_response_time": round(max(response_times), 2),
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
