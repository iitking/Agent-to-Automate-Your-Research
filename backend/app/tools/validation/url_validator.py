import ipaddress
import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


BLOCKED_HOSTNAMES = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"}
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "msclkid", "_ga", "_gl", "mc_cid", "mc_eid"
}


class URLValidationError(ValueError):
    pass


def is_safe_url(url: str) -> bool:
    """Validate that the URL is safe, public, and uses http or https (prevent SSRF)."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return False

        if hostname in BLOCKED_HOSTNAMES or hostname.endswith(".local") or hostname.endswith(".internal"):
            return False

        # Attempt to parse as IP to check private ranges
        try:
            ip = ipaddress.ip_address(hostname)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
            ):
                return False
        except ValueError:
            # Not an IP literal, standard hostname
            pass

        return True
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """Normalize a URL: lowercase hostname, remove tracking queries, strip fragments."""
    try:
        parsed = urlparse(url.strip())
        if not parsed.scheme or not parsed.netloc:
            return url.strip()

        # Clean query parameters
        query_pairs = parse_qsl(parsed.query, keep_blank_values=False)
        cleaned_pairs = [
            (k, v) for k, v in query_pairs if k.lower() not in TRACKING_PARAMS
        ]
        cleaned_query = urlencode(cleaned_pairs)

        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            parsed.params,
            cleaned_query,
            ""  # Strip fragment
        ))
        return normalized.rstrip("/")
    except Exception:
        return url.strip()
