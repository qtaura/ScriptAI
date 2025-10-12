"""
Security utilities for ScriptAI
Handles input validation, sanitization, and rate limiting
"""

import re
import time
import hashlib
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
import html

class SecurityManager:
    """Manages security features for ScriptAI"""
    
    def __init__(self, max_prompt_length: int = 1000, rate_limit: int = 100):
        self.max_prompt_length = max_prompt_length
        self.rate_limit = rate_limit
        self.rate_limit_window = 3600  # 1 hour in seconds
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Dangerous patterns to detect
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'data:text/html',  # Data URLs
            r'vbscript:',  # VBScript
            r'on\w+\s*=',  # Event handlers
            r'<iframe[^>]*>',  # Iframes
            r'<object[^>]*>',  # Objects
            r'<embed[^>]*>',  # Embeds
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
    
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
            return False, f"Prompt too long. Maximum {self.max_prompt_length} characters allowed"
        
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
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'vbscript:', '', sanitized, flags=re.IGNORECASE)
        
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
        while (self.request_counts[client_ip] and 
               self.request_counts[client_ip][0] < current_time - self.rate_limit_window):
            self.request_counts[client_ip].popleft()
        
        # Check if within rate limit
        if len(self.request_counts[client_ip]) >= self.rate_limit:
            return False, f"Rate limit exceeded. Maximum {self.rate_limit} requests per hour"
        
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
        if api_key.startswith('sk-') and len(api_key) > 20:  # OpenAI format
            return True
        if api_key.startswith('hf_') and len(api_key) > 20:  # HuggingFace format
            return True
        if len(api_key) > 20:  # Generic long key
            return True
        
        return False
    
    def log_security_event(self, event_type: str, details: str, client_ip: Optional[str] = None):
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
            "total_requests_last_hour": sum(len(requests) for requests in self.request_counts.values()),
            "rate_limit": self.rate_limit,
            "max_prompt_length": self.max_prompt_length
        }
