"""
Security utilities for ScriptAI
Handles input validation, sanitization, and rate limiting
"""

import re
import time
import hashlib
import hmac
import os
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
import html


class SecurityManager:
    """Manages security features for ScriptAI"""

    def __init__(
        self,
        max_prompt_length: int = 1000,
        rate_limit: int = 100,
        signing_secret: Optional[str] = None,
    ):
        self.max_prompt_length = max_prompt_length
        self.rate_limit = rate_limit
        self.rate_limit_window = 3600  # 1 hour in seconds
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque())
        # Signature verification configuration
        self.signature_scheme = "v1"
        self.signature_header = "X-Signature"
        self.signature_timestamp_header = "X-Signature-Timestamp"
        # Resolve signing secret from argument or environment
        self.signing_secret = signing_secret or os.getenv(
            "REQUEST_SIGNATURE_SECRET", os.getenv("SIGNING_SECRET")
        )

        # Dangerous patterns to detect
        self.dangerous_patterns = [
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript URLs
            r"data:text/html",  # Data URLs
            r"vbscript:",  # VBScript
            r"on\w+\s*=",  # Event handlers
            r"<iframe[^>]*>",  # Iframes
            r"<object[^>]*>",  # Objects
            r"<embed[^>]*>",  # Embeds
        ]

        # Compile patterns for efficiency
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns
        ]

    def validate_prompt(self, prompt: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user prompt for security issues

        Args:
            prompt: User input prompt

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not prompt or not prompt.strip():
            return False, "Empty prompt not allowed"

        if len(prompt) > self.max_prompt_length:
            return (
                False,
                f"Prompt too long. Maximum {self.max_prompt_length} characters allowed",
            )

        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(prompt):
                return False, "Potentially dangerous content detected"

        # Check for excessive repetition (potential spam)
        words = prompt.lower().split()
        if len(words) > 10:
            word_counts: Dict[str, int] = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
                if word_counts[word] > len(words) * 0.3:  # More than 30% repetition
                    return False, "Excessive repetition detected"

        return True, None

    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input to prevent XSS and other attacks

        Args:
            text: Input text to sanitize

        Returns:
            Sanitized text
        """
        # HTML escape
        sanitized = html.escape(text)

        # Remove potential script injections
        sanitized = re.sub(
            r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL
        )
        sanitized = re.sub(r"javascript:", "", sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r"vbscript:", "", sanitized, flags=re.IGNORECASE)

        return sanitized.strip()

    def check_rate_limit(self, client_ip: str) -> Tuple[bool, Optional[str]]:
        """
        Check if client has exceeded rate limit

        Args:
            client_ip: Client IP address

        Returns:
            Tuple of (within_limit, error_message)
        """
        current_time = time.time()

        # Clean old requests outside the window
        while (
            self.request_counts[client_ip]
            and self.request_counts[client_ip][0]
            < current_time - self.rate_limit_window
        ):
            self.request_counts[client_ip].popleft()

        # Check if within rate limit
        if len(self.request_counts[client_ip]) >= self.rate_limit:
            return (
                False,
                f"Rate limit exceeded. Maximum {self.rate_limit} requests per hour",
            )

        # Add current request
        self.request_counts[client_ip].append(current_time)
        return True, None

    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate API key format (basic validation)

        Args:
            api_key: API key to validate

        Returns:
            True if valid format
        """
        if not api_key or len(api_key) < 10:
            return False

        # Check for common patterns
        if api_key.startswith("sk-") and len(api_key) > 20:  # OpenAI format
            return True
        if api_key.startswith("hf_") and len(api_key) > 20:  # HuggingFace format
            return True
        if len(api_key) > 20:  # Generic long key
            return True

        return False

    def log_security_event(
        self, event_type: str, details: str, client_ip: Optional[str] = None
    ):
        """
        Log security events for monitoring

        Args:
            event_type: Type of security event
            details: Event details
            client_ip: Client IP if available
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] SECURITY: {event_type} - {details}"
        if client_ip:
            log_entry += f" - IP: {client_ip}"

        # In production, this would go to a proper logging system
        print(log_entry)

    def get_security_stats(self) -> Dict:
        """
        Get security statistics

        Returns:
            Dictionary with security stats
        """
        current_time = time.time()
        active_clients = 0

        for client_ip, requests in self.request_counts.items():
            # Count clients with recent requests
            recent_requests = [req for req in requests if req > current_time - 3600]
            if recent_requests:
                active_clients += 1

        return {
            "active_clients": active_clients,
            "total_requests_last_hour": sum(
                len(requests) for requests in self.request_counts.values()
            ),
            "rate_limit": self.rate_limit,
            "max_prompt_length": self.max_prompt_length,
        }

    # --- Signature-based request verification ---
    def set_signing_secret(self, secret: Optional[str]) -> None:
        """
        Set or update the signing secret used for HMAC verification.
        """
        self.signing_secret = secret

    def is_signature_configured(self) -> bool:
        """
        Returns True if a signing secret is configured.
        """
        return bool(self.signing_secret)

    def _compute_signature(
        self, body: bytes, timestamp: str, scheme: Optional[str] = None
    ) -> str:
        """
        Compute the HMAC SHA256 hex digest for the given payload and timestamp.

        The base string is: "{scheme}:{timestamp}:{body}" and the returned header
        value format is "{scheme}={hexdigest}".
        """
        used_scheme = (scheme or self.signature_scheme).encode("utf-8")
        base = used_scheme + b":" + timestamp.encode("utf-8") + b":" + body
        digest = hmac.new(
            (self.signing_secret or "").encode("utf-8"), base, hashlib.sha256
        ).hexdigest()
        return f"{(scheme or self.signature_scheme)}={digest}"

    def sign_payload(
        self, body: bytes, timestamp: Optional[int] = None, scheme: Optional[str] = None
    ) -> str:
        """
        Produce an HMAC signature header value for a request body.

        Returns a string like "v1=<hex>". If no timestamp is provided, current
        epoch seconds are used.
        """
        ts = str(int(timestamp if timestamp is not None else time.time()))
        return self._compute_signature(body, ts, scheme)

    def verify_request_signature(
        self,
        headers: Dict[str, str],
        body: bytes,
        client_ip: Optional[str] = None,
        tolerance_seconds: int = 300,
        require: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify HMAC-based request signature.

        - Expects headers `X-Signature` (e.g., "v1=<hex>") and `X-Signature-Timestamp` (epoch seconds).
        - Uses `{scheme}:{timestamp}:{body}` as the message for HMAC SHA256.
        - Returns (True, None) if signature is valid, or if not configured and `require` is False.

        Args:
            headers: Request headers mapping (case-insensitive where possible).
            body: Raw request body bytes used for signature calculation.
            client_ip: Optional client IP for logging.
            tolerance_seconds: Allowed clock skew for timestamp verification.
            require: If True, fail when signature or secret is missing/invalid.
        """
        # Resolve secret at verification time to allow env changes without restart
        if not self.signing_secret:
            self.signing_secret = os.getenv(
                "REQUEST_SIGNATURE_SECRET", os.getenv("SIGNING_SECRET")
            )

        # If signature verification isn't configured, allow unless strictly required
        if not self.signing_secret:
            if require:
                msg = "Signature required but no signing secret configured"
                self.log_security_event("signature_missing_secret", msg, client_ip)
                return False, msg
            return True, None

        # Extract headers
        sig_header = headers.get(self.signature_header) or headers.get(
            self.signature_header.lower()
        )
        ts_header = headers.get(self.signature_timestamp_header) or headers.get(
            self.signature_timestamp_header.lower()
        )

        if not sig_header:
            msg = "Missing X-Signature header"
            if require:
                self.log_security_event("signature_missing", msg, client_ip)
                return False, msg
            # If not required, skip verification
            return True, None

        if not ts_header:
            msg = "Missing X-Signature-Timestamp header"
            self.log_security_event("signature_missing_timestamp", msg, client_ip)
            return False, msg

        # Parse signature header scheme=value
        try:
            if "=" in sig_header:
                scheme, provided_digest = sig_header.split("=", 1)
            else:
                scheme, provided_digest = self.signature_scheme, sig_header
            scheme = scheme.strip()
            provided_digest = provided_digest.strip()
        except Exception:
            msg = "Invalid X-Signature format"
            self.log_security_event("signature_bad_format", msg, client_ip)
            return False, msg

        # Validate timestamp window
        try:
            ts_int = int(ts_header)
        except ValueError:
            msg = "Invalid X-Signature-Timestamp (must be epoch seconds)"
            self.log_security_event("signature_bad_timestamp", msg, client_ip)
            return False, msg

        now = int(time.time())
        if abs(now - ts_int) > tolerance_seconds:
            msg = "Signature timestamp outside allowable window"
            self.log_security_event("signature_timestamp_out_of_window", msg, client_ip)
            return False, msg

        # Compute expected digest and compare
        expected = self._compute_signature(body, str(ts_int), scheme)
        try:
            expected_digest = expected.split("=", 1)[1]
        except Exception:
            msg = "Internal signature computation error"
            self.log_security_event("signature_internal_error", msg, client_ip)
            return False, msg

        if not hmac.compare_digest(provided_digest, expected_digest):
            msg = "Signature mismatch"
            self.log_security_event("signature_mismatch", msg, client_ip)
            return False, msg

        return True, None
