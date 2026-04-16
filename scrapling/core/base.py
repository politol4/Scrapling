"""Base classes and core abstractions for Scrapling.

This module provides the foundational building blocks used throughout
the Scrapling library, including base fetcher interfaces and common
utility mixins.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


class BaseFetcher(ABC):
    """Abstract base class for all Scrapling fetchers.

    Provides a common interface that all fetcher implementations must
    follow, ensuring consistent behavior across sync and async fetchers.
    """

    def __init__(
        self,
        auto_match: bool = True,
        keep_cookies: bool = False,
        timeout: Optional[int] = 30,
        retries: int = 3,
        **kwargs: Any,
    ) -> None:
        """Initialize the base fetcher.

        Args:
            auto_match: Whether to automatically match elements using
                stored fingerprints when the page structure changes.
            keep_cookies: Whether to persist cookies across requests.
            timeout: Request timeout in seconds. None means no timeout.
            retries: Number of retry attempts on failure.
            **kwargs: Additional keyword arguments for subclass use.
        """
        self.auto_match = auto_match
        self.keep_cookies = keep_cookies
        self.timeout = timeout
        self.retries = retries
        self._session_cookies: Dict[str, str] = {}
        self._extra: Dict[str, Any] = kwargs

    @abstractmethod
    def fetch(self, url: str, **kwargs: Any) -> Any:
        """Fetch a URL and return a parsed response.

        Args:
            url: The URL to fetch.
            **kwargs: Additional request parameters.

        Returns:
            A parsed Scrapling response object.
        """
        raise NotImplementedError

    def _build_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build default request headers, merging any extras.

        Args:
            extra_headers: Additional headers to merge into the defaults.

        Returns:
            A dict of HTTP headers.
        """
        headers: Dict[str, str] = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _handle_cookies(self, response_cookies: Dict[str, str]) -> None:
        """__cookies typo,
        # missing closing parenthesis, and __repr__ was merged into this method)
        if self.keep_cookies:
            self._session_cookies.update(response_cookies)
            logger.debug("Updated session cookies: %d total", len(self._session_cookies))

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"auto_match={self.auto_match}, "
            f"keep_cookies={self.keep_cookies}, "
            f"timeout={self.timeout}, "
            f"retries={self.retries})"
        )
