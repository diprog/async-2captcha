from typing import Optional, Dict, Any
from urllib.parse import urlparse


def parse_proxy_url(proxy_url: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Parse a proxy URL (e.g. socks5://user:pass@1.2.3.4:1080) into
    a dictionary matching the 2captcha proxy fields:

    - proxyType (http, socks4, or socks5)
    - proxyAddress
    - proxyPort
    - proxyLogin (optional)
    - proxyPassword (optional)

    If the provided proxy URL is None, returns None.

    :param proxy_url: A string representing the proxy URL or None.
    :return: A dictionary with keys:
        {
            "proxyType": str,
            "proxyAddress": str,
            "proxyPort": int,
            "proxyLogin": Optional[str],
            "proxyPassword": Optional[str],
        }
        or None if proxy_url is None.
    :raises ValueError: If the URL is missing required components
                       or has an unsupported scheme.
    """
    if proxy_url is None:
        return None

    parsed = urlparse(proxy_url)

    scheme = (parsed.scheme or "").lower()
    if scheme not in ("http", "socks4", "socks5"):
        raise ValueError(
            f"Unsupported proxy type: '{scheme}'. "
            "Must be one of: http, socks4, socks5."
        )

    if not parsed.hostname:
        raise ValueError("Proxy address (hostname) is missing.")

    if not parsed.port:
        raise ValueError("Proxy port is missing.")

    return {
        "proxyType": scheme,
        "proxyAddress": parsed.hostname,
        "proxyPort": parsed.port,
        "proxyLogin": parsed.username,
        "proxyPassword": parsed.password,
    }
