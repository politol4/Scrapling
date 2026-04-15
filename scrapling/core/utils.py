"""Utility functions and helpers for Scrapling."""

import re
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return a logger for Scrapling.

    Args:
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log = logging.getLogger("scrapling")
    log.setLevel(level)
    return log


def is_valid_url(url: str) -> bool:
    """Check whether a given string is a valid HTTP/HTTPS URL.

    Args:
        url: The URL string to validate.

    Returns:
        True if valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except ValueError:
        return False


def normalize_url(base: str, href: str) -> str:
    """Resolve a potentially relative URL against a base URL.

    Args:
        base: The base URL of the page.
        href: The href value found in the document.

    Returns:
        An absolute URL string.
    """
    if is_valid_url(href):
        return href
    return urljoin(base, href)


def clean_text(text: str) -> str:
    """Strip excess whitespace and normalize newlines in a text string.

    Args:
        text: Raw text content.

    Returns:
        Cleaned text with collapsed whitespace.
    """
    if not text:
        return ""
    # Collapse multiple whitespace characters into a single space
    text = re.sub(r"[\t\r\f\v]+", " ", text)
    text = re.sub(r" {2,}", " ", text)
    # Normalize multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def flatten(nested: List[Any]) -> List[Any]:
    """Recursively flatten a nested list into a single list.

    Args:
        nested: A potentially nested list.

    Returns:
        A flat list containing all leaf elements.
    """
    result: List[Any] = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def merge_dicts(*dicts: Optional[Dict]) -> Dict:
    """Merge multiple dictionaries, with later ones taking precedence.

    None values in the input are silently ignored.

    Args:
        *dicts: Dictionaries to merge.

    Returns:
        A single merged dictionary.
    """
    merged: Dict = {}
    for d in dicts:
        if d:
            merged.update(d)
    return merged


def extract_domain(url: str) -> str:
    """Extract the domain (netloc) from a URL string.

    Args:
        url: A full URL.

    Returns:
        The netloc portion (e.g. 'example.com'), or empty string on failure.
    """
    try:
        return urlparse(url).netloc
    except ValueError:
        return ""


def slugify(text: str) -> str:
    """Convert a string to a URL-friendly slug.

    Args:
        text: Input string.

    Returns:
        Lowercased, hyphen-separated slug.
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text
