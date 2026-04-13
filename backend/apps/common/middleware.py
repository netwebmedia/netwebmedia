"""Security middleware for hardened HTTP headers, RLS, and request protection."""

import time
import logging

from django.conf import settings
from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger("security")


class SecurityHeadersMiddleware:
    """Adds comprehensive security headers to every response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Prevent MIME-type sniffing
        response["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking (defense-in-depth alongside CSP frame-ancestors)
        response["X-Frame-Options"] = "DENY"

        # Control referrer information leakage
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Restrict browser features/APIs
        response["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )

        # Content Security Policy
        csp = getattr(settings, "CONTENT_SECURITY_POLICY", None)
        if csp:
            response["Content-Security-Policy"] = csp

        # Cross-Origin policies
        response["Cross-Origin-Opener-Policy"] = "same-origin"
        response["Cross-Origin-Resource-Policy"] = "same-origin"
        response["Cross-Origin-Embedder-Policy"] = "require-corp"

        # Cache control for authenticated API responses
        if request.path.startswith("/api/") and request.user.is_authenticated:
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response["Pragma"] = "no-cache"

        return response


class RateLimitMiddleware:
    """
    Simple global rate limiter per IP address.
    Uses in-memory storage — for production, swap to Redis.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._hits = {}  # ip -> [(timestamp, ...)]
        self.window = getattr(settings, "RATE_LIMIT_WINDOW", 60)  # seconds
        self.max_requests = getattr(settings, "RATE_LIMIT_MAX_REQUESTS", 100)

    def _get_client_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")

    def __call__(self, request):
        # Skip rate limiting for non-API requests
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        ip = self._get_client_ip(request)
        now = time.monotonic()
        cutoff = now - self.window

        # Clean old entries and add current
        hits = [t for t in self._hits.get(ip, []) if t > cutoff]
        hits.append(now)
        self._hits[ip] = hits

        if len(hits) > self.max_requests:
            logger.warning("Rate limit exceeded for IP %s", ip)
            return JsonResponse(
                {"detail": "Rate limit exceeded. Try again later."},
                status=429,
                headers={"Retry-After": str(self.window)},
            )

        response = self.get_response(request)
        response["X-RateLimit-Limit"] = str(self.max_requests)
        response["X-RateLimit-Remaining"] = str(max(0, self.max_requests - len(hits)))
        return response


class OrganizationRLSMiddleware:
    """
    Sets the PostgreSQL session variable `app.current_organization_id` so that
    RLS policies can enforce row-level tenant isolation at the database level.

    Must run AFTER AuthenticationMiddleware so request.user is available.
    The organization is resolved from the X-Organization-Slug header,
    query param, or cached membership.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if connection.vendor == "postgresql" and hasattr(request, "user") and request.user.is_authenticated:
            org = getattr(request, "_cached_organization", None)
            if org:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT set_config('app.current_organization_id', %s, TRUE)",
                        [str(org.pk)],
                    )
            else:
                # Clear the variable so RLS blocks everything
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT set_config('app.current_organization_id', '', TRUE)",
                        [],
                    )

        return self.get_response(request)


class RequestSizeLimitMiddleware:
    """Rejects request bodies that exceed MAX_REQUEST_BODY_SIZE."""

    def __init__(self, get_response):
        self.get_response = get_response
        # Default: 2 MB
        self.max_size = getattr(settings, "MAX_REQUEST_BODY_SIZE", 2 * 1024 * 1024)

    def __call__(self, request):
        content_length = request.META.get("CONTENT_LENGTH")
        if content_length:
            try:
                if int(content_length) > self.max_size:
                    return JsonResponse(
                        {"detail": "Request body too large."},
                        status=413,
                    )
            except (ValueError, TypeError):
                pass
        return self.get_response(request)
