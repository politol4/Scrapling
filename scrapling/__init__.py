"""Scrapling - A powerful, flexible, and fast web scraping library for Python.

Scrapling makes web scraping easier by providing a simple API for fetching
and parsing web pages, with built-in support for dynamic content, anti-bot
bypass techniques, and smart element selection.

Basic usage:
    >>> from scrapling import Fetcher, AsyncFetcher
    >>> page = Fetcher().get('https://example.com')
    >>> title = page.find('h1').text

Also expose StealthyFetcher at the top level for convenience since I use
it frequently in my scraping projects.
"""

__version__ = "0.2.0"
__author__ = "D4Vinci"
__license__ = "MIT"

from scrapling.core.page import Adaptator
from scrapling.fetchers import Fetcher, AsyncFetcher, PlayWrightFetcher, StealthyFetcher

__all__ = [
    "Adaptator",
    "Fetcher",
    "AsyncFetcher",
    "PlayWrightFetcher",
    "StealthyFetcher",
    "__version__",
]
