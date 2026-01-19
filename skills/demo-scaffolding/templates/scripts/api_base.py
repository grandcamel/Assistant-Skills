#!/usr/bin/env python3
"""
{{PRODUCT}} API Base Module

Shared utilities for {{PRODUCT}} API scripts including authentication,
configuration, and common operations.

Environment Variables:
    {{API_URL_VAR}}: {{PRODUCT}} API URL
    {{API_TOKEN_VAR}}: API token
"""

import os
import sys
import time
from functools import wraps

import requests

# Retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0  # seconds
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def retry_on_failure(max_retries: int = DEFAULT_MAX_RETRIES, base_delay: float = DEFAULT_BASE_DELAY):
    """
    Decorator for retrying API calls with exponential backoff.

    Handles:
    - 429 Too Many Requests (rate limiting)
    - 5xx Server errors (transient failures)
    - Connection errors

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (doubles each attempt)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    response = func(*args, **kwargs)
                    if response.status_code not in RETRYABLE_STATUS_CODES:
                        return response

                    # Retryable status code
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        # Respect Retry-After header if present
                        if response.status_code == 429:
                            retry_after = response.headers.get("Retry-After")
                            if retry_after:
                                delay = max(delay, float(retry_after))
                        print(f"  Retry {attempt + 1}/{max_retries} after {delay:.1f}s (status {response.status_code})")
                        time.sleep(delay)
                    else:
                        return response

                except requests.exceptions.ConnectionError as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        print(f"  Retry {attempt + 1}/{max_retries} after {delay:.1f}s (connection error)")
                        time.sleep(delay)
                    else:
                        raise
                except requests.exceptions.Timeout as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        print(f"  Retry {attempt + 1}/{max_retries} after {delay:.1f}s (timeout)")
                        time.sleep(delay)
                    else:
                        raise

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry loop completed without result")

        return wrapper
    return decorator


class {{PRODUCT_UPPER}}Config:
    """Configuration loaded from environment variables."""

    def __init__(self):
        self.api_url = os.environ.get("{{API_URL_VAR}}", "").rstrip("/")
        self.api_token = os.environ.get("{{API_TOKEN_VAR}}", "")

    def validate(self) -> bool:
        """Validate required configuration is present."""
        return all([self.api_url, self.api_token])

    def print_status(self):
        """Print configuration status for debugging."""
        print(f"  {{API_URL_VAR}}: {'set' if self.api_url else 'missing'}")
        print(f"  {{API_TOKEN_VAR}}: {'set' if self.api_token else 'missing'}")


class {{PRODUCT_UPPER}}Client:
    """Simple {{PRODUCT}} API client with common operations."""

    def __init__(self, config: {{PRODUCT_UPPER}}Config | None = None):
        self.config = config or {{PRODUCT_UPPER}}Config()
        self._headers = {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json"
        }

    @property
    def headers(self) -> dict:
        """Get headers for requests."""
        return self._headers

    @retry_on_failure()
    def get(self, endpoint: str, params: dict | None = None) -> requests.Response:
        """Make GET request to {{PRODUCT}} API with automatic retry."""
        url = f"{self.config.api_url}{endpoint}"
        return requests.get(url, headers=self.headers, params=params, timeout=30)

    @retry_on_failure()
    def post(self, endpoint: str, json: dict | None = None) -> requests.Response:
        """Make POST request to {{PRODUCT}} API with automatic retry."""
        url = f"{self.config.api_url}{endpoint}"
        return requests.post(url, headers=self.headers, json=json, timeout=30)

    @retry_on_failure()
    def delete(self, endpoint: str) -> requests.Response:
        """Make DELETE request to {{PRODUCT}} API with automatic retry."""
        url = f"{self.config.api_url}{endpoint}"
        return requests.delete(url, headers=self.headers, timeout=30)


def require_config(config: {{PRODUCT_UPPER}}Config | None = None) -> {{PRODUCT_UPPER}}Config:
    """Validate configuration and exit if invalid."""
    cfg = config or {{PRODUCT_UPPER}}Config()
    if not cfg.validate():
        print("Error: Missing required environment variables")
        cfg.print_status()
        sys.exit(1)
    return cfg
