"""Concrete fetcher implementations for Scrapling.

This module provides ready-to-use fetcher classes built on top of BaseFetcher,
covering common HTTP fetching strategies including plain requests, and
browser-based fetching via Playwright.
"""

import logging
from typing import Any, Dict, Optional, Union

import httpx

from scrapling.core.base import BaseFetcher

logger = logging.getLogger(__name__)


class HttpxFetcher(BaseFetcher):
    """A lightweight fetcher backed by httpx.

    Suitable for fetching static pages or APIs that do not require
    JavaScript execution.  Supports both synchronous and asynchronous
    usage via httpx's sync/async clients.

    Example::

        fetcher = HttpxFetcher(headers={"Accept-Language": "en-US"})
        response = fetcher.fetch("https://example.com")
    """

    def __init__(
        self,
        *,
        # Increased default timeout from 30s to 60s to better handle slow sites
        timeout: float = 60.0,
        follow_redirects: bool = True,
        verify_ssl: bool = True,
        proxy: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.verify_ssl = verify_ssl
        self.proxy = proxy

    def _build_client_kwargs(self) -> Dict[str, Any]:
        """Assemble keyword arguments for the httpx client."""
        kwargs: Dict[str, Any] = {
            "timeout": self.timeout,
            "follow_redirects": self.follow_redirects,
            "verify": self.verify_ssl,
            "headers": self._build_headers(),
        }
        if self.proxy:
            kwargs["proxies"] = {"http://": self.proxy, "https://": self.proxy}
        cookies = self._handle_cookies()
        if cookies:
            kwargs["cookies"] = cookies
        return kwargs

    def fetch(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Perform an HTTP request and return the raw httpx Response.

        Args:
            url: Target URL.
            method: HTTP verb (GET, POST, …).
            data: Form-encoded payload for POST requests.
            json: JSON-serialisable payload for POST requests.
            extra_headers: Additional headers merged on top of defaults.

        Returns:
            An :class:`httpx.Response` object.

        Raises:
            httpx.HTTPError: On any network or HTTP-level error.
        """
        client_kwargs = self._build_client_kwargs()
        if extra_headers:
            client_kwargs["headers"] = {
                **client_kwargs.get("headers", {}),
                **extra_headers,
            }

        logger.debug("HttpxFetcher %s %s", method.upper(), url)
        with httpx.Client(**client_kwargs) as client:
            response = client.request(
                method.upper(),
                url,
                data=data,
