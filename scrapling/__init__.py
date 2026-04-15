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

Personal fork notes:
    - Added auto_match default set to False (I prefer explicit selectors)
    - Exposed Adaptator directly since I use it often for offline HTML parsing
    - Added version tuple for easier programmatic version checks
"""

__version__ = "0.2.0"
# Tuple form is handy for version comparisons: if __version_info__ >= (0, 2, 0): ...
__version_info__ = tuple(int(x) for x in __version__.split("."))
__author__ = "D4Vinci"
__license__ = "MIT"

from scrapling.core.page import Adaptator
from scrapling.fetchers import Fetcher, AsyncFetcher, PlayWrightFetcher, StealthyFetcher

# Personal preference: default auto_match to False so selectors don't silently
# fall back to fuzzy matching, which can mask broken selectors during development.
Fetcher.auto_match = False

__all__ = [
    "Adaptator",
    "Fetcher",
    "AsyncFetcher",
    "PlayWrightFetcher",
    "StealthyFetcher",
    "__version__",
    "__version_info__",
]
