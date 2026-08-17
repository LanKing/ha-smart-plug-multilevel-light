#!/usr/bin/env python3
"""Convert relative README navigation links to absolute GitHub URLs.

Image sources are intentionally left untouched. This is needed because HACS and
other embedded Markdown renderers do not always resolve relative navigation
links the same way GitHub does.
"""

from __future__ import annotations

import posixpath
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPOSITORY_URL = "https://github.com/LanKing/ha-smart-plug-multilevel-light"
DEFAULT_BRANCH = "main"

HTML_LINK_RE = re.compile(
    r'(?P<prefix><a\b[^>]*?\bhref=)(?P<quote>["\'])(?P<url>.*?)(?P=quote)',
    re.IGNORECASE,
)
MARKDOWN_LINK_RE = re.compile(
    r'(?<!!)'
    r'(?P<prefix>\[[^\]]*\]\()'
    r'(?P<url><[^>]+>|[^\s)]+)'
    r'(?P<suffix>[^)]*\))'
)
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def is_relative_navigation_link(url: str) -> bool:
    """Return True only for relative navigation links, never images/anchors."""
    value = url.strip()
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1]
    if not value or value.startswith(("#", "/", "//")):
        return False
    if SCHEME_RE.match(value):
        return False
    return True


def absolute_url(readme: Path, url: str) -> str:
    """Resolve a relative URL against a README and return a GitHub blob URL."""
    wrapped = url.startswith("<") and url.endswith(">")
    value = url[1:-1] if wrapped else url
    parts = urlsplit(value)

    if not parts.path:
        return url

    readme_dir = readme.parent.relative_to(ROOT).as_posix()
    base = "" if readme_dir == "." else readme_dir
    resolved = posixpath.normpath(posixpath.join(base, parts.path))

    if resolved == ".." or resolved.startswith("../"):
        raise ValueError(f"Link escapes repository root in {readme}: {url}")

    result = urlunsplit(
        (
            "https",
            "github.com",
            f"/LanKing/ha-smart-plug-multilevel-light/blob/{DEFAULT_BRANCH}/{resolved}",
            parts.query,
            parts.fragment,
        )
    )
    return f"<{result}>" if wrapped else result


def normalize_line(readme: Path, line: str) -> tuple[str, int]:
    converted = 0

    def replace_html(match: re.Match[str]) -> str:
        nonlocal converted
        url = match.group("url")
        if not is_relative_navigation_link(url):
            return match.group(0)
        converted += 1
        return (
            f'{match.group("prefix")}{match.group("quote")}'
            f'{absolute_url(readme, url)}{match.group("quote")}'
        )

    line = HTML_LINK_RE.sub(replace_html, line)

    def replace_markdown(match: re.Match[str]) -> str:
        nonlocal converted
        url = match.group("url")
        if not is_relative_navigation_link(url):
            return match.group(0)
        converted += 1
        return (
            f'{match.group("prefix")}{absolute_url(readme, url)}'
            f'{match.group("suffix")}'
        )

    line = MARKDOWN_LINK_RE.sub(replace_markdown, line)
    return line, converted


def normalize_readme(readme: Path) -> tuple[bool, int]:
    original = readme.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    updated: list[str] = []
    in_fence = False
    converted = 0

    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            updated.append(line)
            continue
        if in_fence:
            updated.append(line)
            continue
        normalized, count = normalize_line(readme, line)
        converted += count
        updated.append(normalized)

    result = "".join(updated)
    if result == original:
        return False, converted
    readme.write_text(result, encoding="utf-8")
    return True, converted


def remaining_relative_links(readme: Path) -> list[str]:
    """Return relative navigation links still present outside fenced code blocks."""
    found: list[str] = []
    in_fence = False
    for line in readme.read_text(encoding="utf-8").splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in HTML_LINK_RE.finditer(line):
            url = match.group("url")
            if is_relative_navigation_link(url):
                found.append(url)
        for match in MARKDOWN_LINK_RE.finditer(line):
            url = match.group("url")
            if is_relative_navigation_link(url):
                found.append(url)
    return found


def main() -> int:
    readmes = [ROOT / "README.md", *sorted(DOCS.glob("README_*.md"))]
    total = 0

    for readme in readmes:
        changed, converted = normalize_readme(readme)
        total += converted
        if changed:
            print(f"{readme.relative_to(ROOT)}: converted {converted} link(s)")

    leftovers = {
        str(readme.relative_to(ROOT)): links
        for readme in readmes
        if (links := remaining_relative_links(readme))
    }
    if leftovers:
        for path, links in leftovers.items():
            print(f"ERROR {path}: relative links remain: {links}")
        return 1

    print(f"Converted {total} relative navigation link(s); image paths were not changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
