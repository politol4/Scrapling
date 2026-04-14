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
        timeout: float = 30.0,
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
                json=json,
            )
            response.raise_for_status()
            return response


class PlaywrightFetcher(BaseFetcher):
    """A JavaScript-capable fetcher backed by Playwright.

    Uses a headless Chromium browser to render pages, making it suitable
    for SPAs and pages that rely heavily on client-side JavaScript.

    Playwright must be installed separately::

        pip install playwright && playwright install chromium

    Example::

        fetcher = PlaywrightFetcher(headless=True)
        html = fetcher.fetch("https://example.com")
    """

    def __init__(
        self,
        *,
        headless: bool = True,
        wait_until: str = "domcontentloaded",
        timeout: float = 30_000,  # milliseconds, Playwright convention
        proxy: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.headless = headless
        self.wait_until = wait_until
        self.timeout = timeout
        self.proxy = proxy

    def fetch(self, url: str, **kwargs: Any) -> str:  # type: ignore[override]
        """Navigate to *url* and return the fully-rendered HTML source.

        Args:
            url: Target URL.
            **kwargs: Forwarded to ``page.goto``.

        Returns:
            The page's outer HTML as a string.

        Raises:
            ImportError: When the ``playwright`` package is not installed.
            playwright.sync_api.Error: On navigation or browser errors.
        """
        try:
            from playwright.sync_api import sync_playwright  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "Playwright is required for PlaywrightFetcher. "
                "Install it with: pip install playwright && playwright install chromium"
            ) from exc

        launch_opts: Dict[str, Any] = {"headless": self.headless}
        if self.proxy:
            launch_opts["proxy"] = {"server": self.proxy}

        logger.debug("PlaywrightFetcher GET %s (headless=%s)", url, self.headless)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_opts)
            context = browser.new_context(
                extra_http_headers=self._build_headers(),
            )
            page = context.new_page()
            page.goto(
                url,
                wait_until=self.wait_until,
                timeout=self.timeout,
                **kwargs,
            )
            html = page.content()
            browser.close()
        return html
