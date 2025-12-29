"""
Error Handling for Assistant Skills

Provides:
- Exception hierarchy for API errors
- Error handling decorator
- Error sanitization for sensitive data
- Formatted error output

Usage:
    from error_handler import handle_errors, APIError, print_error

    @handle_errors
    def main():
        # Your code here
        pass
"""

import sys
import re
import functools
import traceback
from typing import Optional, Callable, Any

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class APIError(Exception):
    """Base exception for all API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
        operation: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        self.operation = operation
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = []
        if self.operation:
            parts.append(f"[{self.operation}]")
        if self.status_code:
            parts.append(f"({self.status_code})")
        parts.append(self.message)
        return " ".join(parts)


class AuthenticationError(APIError):
    """Raised when authentication fails (401)."""
    pass


class PermissionError(APIError):
    """Raised when user lacks permission (403)."""
    pass


class ValidationError(APIError):
    """Raised for invalid input or bad requests (400)."""
    pass


class NotFoundError(APIError):
    """Raised when resource is not found (404)."""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ConflictError(APIError):
    """Raised on resource conflicts (409)."""
    pass


class ServerError(APIError):
    """Raised for server-side errors (5xx)."""
    pass


def sanitize_error_message(message: str) -> str:
    """
    Remove sensitive information from error messages.

    Args:
        message: The error message to sanitize

    Returns:
        Sanitized message with sensitive data removed
    """
    # Patterns to sanitize
    patterns = [
        # API tokens (various formats)
        (r'(?i)(api[_-]?token|token|apikey|api[_-]?key)["\s:=]+[A-Za-z0-9_\-]{10,}', r'\1=[REDACTED]'),
        # Email addresses in auth context
        (r'(?i)(auth|email|user)["\s:=]+[\w.+-]+@[\w.-]+', r'\1=[REDACTED]'),
        # Bearer tokens
        (r'Bearer\s+[A-Za-z0-9_\-\.]+', 'Bearer [REDACTED]'),
        # Basic auth base64
        (r'Basic\s+[A-Za-z0-9+/=]+', 'Basic [REDACTED]'),
        # URLs with credentials
        (r'https?://[^:]+:[^@]+@', 'https://[REDACTED]@'),
        # Session IDs
        (r'(?i)(session[_-]?id|jsessionid)["\s:=]+[A-Za-z0-9_\-]+', r'\1=[REDACTED]'),
        # Generic secrets
        (r'(?i)(secret|password|passwd|pwd)["\s:=]+[^\s"\']+', r'\1=[REDACTED]'),
    ]

    sanitized = message
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized)

    return sanitized


def extract_error_message(response: Any) -> str:
    """
    Extract a meaningful error message from an API response.

    Args:
        response: The HTTP response object

    Returns:
        Extracted error message
    """
    try:
        data = response.json()

        # Common error formats

        # Format: {"errors": [...]}
        if "errors" in data:
            errors = data["errors"]
            if isinstance(errors, list) and errors:
                error = errors[0]
                return error.get("title", error.get("detail", error.get("message", str(error))))
            return str(errors)

        # Format: {"message": "..."}
        if "message" in data:
            return data["message"]

        # Format: {"error": "..."}
        if "error" in data:
            err = data["error"]
            if isinstance(err, dict):
                return err.get("message", str(err))
            return str(err)

        # Format: {"errorMessage": "..."}
        if "errorMessage" in data:
            return data["errorMessage"]

        # Format: {"detail": "..."}
        if "detail" in data:
            return data["detail"]

        return str(data)

    except (ValueError, KeyError, AttributeError):
        if hasattr(response, 'text'):
            return response.text[:500] if response.text else f"HTTP {response.status_code}"
        return str(response)


def handle_api_error(
    response: Any,
    operation: str = "API request",
) -> None:
    """
    Handle an error response from an API.

    Args:
        response: The HTTP response object
        operation: Description of the operation for error context

    Raises:
        Appropriate APIError subclass based on status code
    """
    status_code = response.status_code
    message = extract_error_message(response)
    message = sanitize_error_message(message)

    error_kwargs = {
        "message": message,
        "status_code": status_code,
        "response": response,
        "operation": operation,
    }

    if status_code == 400:
        raise ValidationError(**error_kwargs)
    elif status_code == 401:
        raise AuthenticationError(
            message="Authentication failed. Check your credentials.",
            **{k: v for k, v in error_kwargs.items() if k != "message"}
        )
    elif status_code == 403:
        raise PermissionError(
            message=f"Permission denied: {message}",
            **{k: v for k, v in error_kwargs.items() if k != "message"}
        )
    elif status_code == 404:
        raise NotFoundError(**error_kwargs)
    elif status_code == 409:
        raise ConflictError(**error_kwargs)
    elif status_code == 429:
        retry_after = None
        if hasattr(response, 'headers'):
            retry_after_str = response.headers.get("Retry-After")
            if retry_after_str and retry_after_str.isdigit():
                retry_after = int(retry_after_str)
        raise RateLimitError(
            message=f"Rate limit exceeded. Retry after {retry_after or 'unknown'} seconds.",
            retry_after=retry_after,
            **{k: v for k, v in error_kwargs.items() if k != "message"}
        )
    elif 500 <= status_code < 600:
        raise ServerError(
            message=f"Server error: {message}",
            **{k: v for k, v in error_kwargs.items() if k != "message"}
        )
    else:
        raise APIError(**error_kwargs)


def print_error(
    message: str,
    error: Optional[Exception] = None,
    suggestion: Optional[str] = None,
    show_traceback: bool = False,
) -> None:
    """
    Print a formatted error message to stderr.

    Args:
        message: The main error message
        error: Optional exception object
        suggestion: Optional suggestion for resolution
        show_traceback: Whether to print the full traceback
    """
    print(f"\n[ERROR] {message}", file=sys.stderr)

    if error:
        error_str = sanitize_error_message(str(error))
        print(f"  Details: {error_str}", file=sys.stderr)

        if isinstance(error, AuthenticationError):
            print("  Hint: Check your API credentials/token", file=sys.stderr)
        elif isinstance(error, PermissionError):
            print("  Hint: Verify you have access to this resource", file=sys.stderr)
        elif isinstance(error, RateLimitError) and error.retry_after:
            print(f"  Hint: Wait {error.retry_after} seconds before retrying", file=sys.stderr)
        elif isinstance(error, NotFoundError):
            print("  Hint: Check that the resource ID/key is correct", file=sys.stderr)

    if suggestion:
        print(f"  Suggestion: {suggestion}", file=sys.stderr)

    if show_traceback and error:
        print("\n  Traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    print("", file=sys.stderr)


def handle_errors(func: Callable) -> Callable:
    """
    Decorator to handle errors in main functions.

    Catches exceptions and prints formatted error messages,
    then exits with appropriate status code.

    Usage:
        @handle_errors
        def main():
            # Your code here
            pass

    Args:
        func: The function to wrap

    Returns:
        Wrapped function with error handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.", file=sys.stderr)
            sys.exit(130)
        except AuthenticationError as e:
            print_error("Authentication failed", e)
            sys.exit(1)
        except PermissionError as e:
            print_error("Permission denied", e)
            sys.exit(1)
        except ValidationError as e:
            print_error("Invalid input", e)
            sys.exit(1)
        except NotFoundError as e:
            print_error("Resource not found", e)
            sys.exit(1)
        except RateLimitError as e:
            print_error("Rate limit exceeded", e)
            sys.exit(1)
        except ConflictError as e:
            print_error("Conflict error", e)
            sys.exit(1)
        except ServerError as e:
            print_error("Server error", e)
            sys.exit(1)
        except APIError as e:
            print_error("API error", e)
            sys.exit(1)
        except Exception as e:
            # Handle requests exceptions if available
            if HAS_REQUESTS:
                if isinstance(e, requests.exceptions.ConnectionError):
                    print_error(
                        "Connection failed",
                        e,
                        suggestion="Check your network connection and API URL"
                    )
                    sys.exit(1)
                elif isinstance(e, requests.exceptions.Timeout):
                    print_error(
                        "Request timed out",
                        e,
                        suggestion="The server took too long to respond. Try again later."
                    )
                    sys.exit(1)

            print_error(
                "Unexpected error",
                e,
                show_traceback=True
            )
            sys.exit(1)

    return wrapper


class ErrorContext:
    """
    Context manager for error handling with custom messages.

    Usage:
        with ErrorContext("creating resource", resource_id=id):
            client.post("/api/resources", data=resource_data)
    """

    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and issubclass(exc_type, APIError):
            # Enhance error message with context
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            exc_val.operation = f"{self.operation} ({context_str})" if context_str else self.operation
        return False  # Don't suppress the exception
