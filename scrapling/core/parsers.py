"""HTML parsing utilities for Scrapling.

Provides response parsing, element extraction, and data transformation
functionalities built on top of lxml and cssselect.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterator, List, Optional, Union

from lxml import etree, html
from lxml.html import HtmlElement


class ParsedElement:
    """Wrapper around an lxml HtmlElement with a friendlier API."""

    def __init__(self, element: HtmlElement, base_url: str = "") -> None:
        self._element = element
        self.base_url = base_url

    # ------------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------------

    @property
    def text(self) -> str:
        """Return the direct text content of this element (no children)."""
        return (self._element.text or "").strip()

    @property
    def full_text(self) -> str:
        """Return all text content including descendant elements."""
        return (self._element.text_content() or "").strip()

    # ------------------------------------------------------------------
    # Attribute helpers
    # ------------------------------------------------------------------

    def get(self, attr: str, default: Optional[str] = None) -> Optional[str]:
        """Get an element attribute value."""
        return self._element.get(attr, default)

    @property
    def attrs(self) -> Dict[str, str]:
        """Return all attributes as a plain dict."""
        return dict(self._element.attrib)

    @property
    def tag(self) -> str:
        """Return the element tag name."""
        return self._element.tag

    # ------------------------------------------------------------------
    # Selection helpers
    # ------------------------------------------------------------------

    def css(self, selector: str) -> List["ParsedElement"]:
        """Select child elements using a CSS selector."""
        return [
            ParsedElement(el, self.base_url)
            for el in self._element.cssselect(selector)
        ]

    def xpath(self, query: str) -> List[Union["ParsedElement", str]]:
        """Select elements or values using an XPath expression."""
        results = self._element.xpath(query)
        return [
            ParsedElement(r, self.base_url) if isinstance(r, HtmlElement) else r
            for r in results
        ]

    def css_first(self, selector: str) -> Optional["ParsedElement"]:
        """Return the first element matching *selector*, or ``None``."""
        matches = self.css(selector)
        return matches[0] if matches else None

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ParsedElement tag={self.tag!r} text={self.text[:40]!r}>"

    def __iter__(self) -> Iterator["ParsedElement"]:
        for child in self._element:
            yield ParsedElement(child, self.base_url)


class HTMLParser:
    """Parse raw HTML bytes/strings into a tree of :class:`ParsedElement` objects."""

    def __init__(self, html_content: Union[str, bytes], base_url: str = "") -> None:
        if isinstance(html_content, str):
            html_content = html_content.encode("utf-8", errors="replace")

        self._tree: HtmlElement = html.fromstring(html_content)
        self.base_url = base_url

        # Make absolute links resolvable when a base URL is provided
        if base_url:
            try:
                self._tree.make_links_absolute(base_url, resolve_base_href=True)
            except Exception:  # noqa: BLE001 — best-effort
                pass

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def css(self, selector: str) -> List[ParsedElement]:
        """Select elements from the document root using a CSS selector."""
        return [
            ParsedElement(el, self.base_url)
            for el in self._tree.cssselect(selector)
        ]

    def xpath(self, query: str) -> List[Union[ParsedElement, str]]:
        """Select elements or values from the document root using XPath."""
        results = self._tree.xpath(query)
        return [
            ParsedElement(r, self.base_url) if isinstance(r, HtmlElement) else r
            for r in results
        ]

    def css_first(self, selector: str) -> Optional[ParsedElement]:
        """Return the first element matching *selector*, or ``None``."""
        matches = self.css(selector)
        return matches[0] if matches else None

    # ------------------------------------------------------------------
    # Metadata helpers
    # ------------------------------------------------------------------

    @property
    def title(self) -> str:
        """Return the page ``<title>`` text, or an empty string."""
        el = self.css_first("title")
        return el.full_text if el else ""

    @property
    def links(self) -> List[str]:
        """Return all ``href`` values found in ``<a>`` tags."""
        return [
            el.get("href", "")
            for el in self.css("a[href]")
        ]

    def __repr__(self) -> str:  # pragma: no cover
        return f"<HTMLParser title={self.title!r} base_url={self.base_url!r}>"
