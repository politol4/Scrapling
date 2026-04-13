"""Scrapling - A powerful, flexible, and fast web scraping library for Python.

Scrapling makes web scraping easier by providing a simple API for fetching
and parsing web pages, with built-in support for dynamic content, anti-bot
bypass techniques, and smart element selection.

Basic usage:
    >>> from scrapling import Fetcher, AsyncFetcher
    >>> page = Fetcher().get('https://example.com')
    >>> title = page.find('h1').text
"""

__version__ = "0.2.0"
__author__ = "D4Vinci"
__license__ = "MIT"

from scrapling.core.page import Adaptator
from scrapling.fetchers import Fetcher, AsyncFetcher, PlayWrightFetcher

__all__ = [
    "Adaptator",
    "Fetcher",
    "AsyncFetcher",
    "PlayWrightFetcher",
    "__version__",
]
