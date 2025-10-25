#!/usr/bin/env python3
"""Site Snapshot Crawler for Corp Knowledge Base

Crawls conciergecareadvisors.com per policy, extracts text sections,
saves to config/corp_knowledge.jsonl for FAQ/AI Advisor grounding.

Usage:
    python tools/sync_site.py
    make sync-site
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

# Paths
CONFIG_DIR = Path(__file__).parent.parent / "config"
POLICY_PATH = CONFIG_DIR / "crawl_policy.json"
OUTPUT_PATH = CONFIG_DIR / "corp_knowledge.jsonl"
META_PATH = CONFIG_DIR / "corp_knowledge.meta.json"


def load_policy() -> dict[str, Any]:
    """Load crawl policy from config/crawl_policy.json."""
    with open(POLICY_PATH) as f:
        return json.load(f)


def matches_pattern(url: str, patterns: list[str]) -> bool:
    """Check if URL matches any regex pattern in list."""
    return any(re.search(pat, url) for pat in patterns)


def fetch_sitemap(root: str) -> list[str]:
    """Fetch sitemap.xml and extract URLs."""
    sitemap_url = urljoin(root, "/sitemap.xml")
    try:
        resp = requests.get(sitemap_url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "xml")
        urls = [loc.text for loc in soup.find_all("loc")]
        print(f"✓ Loaded {len(urls)} URLs from sitemap")
        return urls
    except Exception as e:
        print(f"⚠ Sitemap fetch failed: {e}")
        return []


def check_robots(root: str) -> RobotFileParser:
    """Load robots.txt parser."""
    rp = RobotFileParser()
    rp.set_url(urljoin(root, "/robots.txt"))
    try:
        rp.read()
        print("✓ Loaded robots.txt")
    except Exception as e:
        print(f"⚠ robots.txt load failed: {e}")
    return rp


def extract_text_sections(html: str, url: str) -> list[dict[str, Any]]:
    """Extract text sections split by headings (h1-h3)."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove script, style, nav, footer
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Get page title
    title_tag = soup.find("title")
    page_title = title_tag.text.strip() if title_tag else urlparse(url).path

    sections = []
    current_heading = None
    current_text = []

    # Walk through body elements
    body = soup.find("body")
    if not body:
        return []

    for elem in body.descendants:
        if elem.name in ["h1", "h2", "h3"]:
            # Save previous section
            if current_text:
                text = " ".join(current_text).strip()
                if len(text) >= 100:  # Min section length
                    sections.append({
                        "heading": current_heading or page_title,
                        "text": text,
                    })
            # Start new section
            current_heading = elem.get_text(strip=True)
            current_text = []
        elif elem.name == "p" and elem.string:
            current_text.append(elem.get_text(strip=True))

    # Save final section
    if current_text:
        text = " ".join(current_text).strip()
        if len(text) >= 100:
            sections.append({
                "heading": current_heading or page_title,
                "text": text,
            })

    return [
        {
            "title": page_title,
            "heading": sec["heading"],
            "text": sec["text"],
        }
        for sec in sections
    ]


def crawl(policy: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Crawl site per policy, return chunks and metadata."""
    root = policy["root"]
    use_sitemap = policy.get("use_sitemap", True)
    allow = policy.get("allow", [])
    exclude = policy.get("exclude", [])
    max_pages = policy.get("max_pages", 200)
    rate_limit = policy.get("rate_limit_per_sec", 2)
    max_bytes = policy.get("max_bytes_per_page", 300000)
    min_chars = policy.get("min_text_chars", 400)
    respect_robots = policy.get("respect_robots", True)

    # Load robots.txt
    robots = check_robots(root) if respect_robots else None

    # Collect URLs
    if use_sitemap:
        candidate_urls = fetch_sitemap(root)
    else:
        candidate_urls = [root]

    # Filter URLs
    allowed_urls = []
    for url in candidate_urls:
        if exclude and matches_pattern(url, exclude):
            continue
        if allow and not matches_pattern(url, allow):
            continue
        if robots and not robots.can_fetch("*", url):
            print(f"⊘ Blocked by robots.txt: {url}")
            continue
        allowed_urls.append(url)

    allowed_urls = allowed_urls[:max_pages]
    print(f"✓ {len(allowed_urls)} URLs to crawl (after filtering)")

    # Crawl
    chunks = []
    stats = {
        "total_urls": len(allowed_urls),
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "total_chunks": 0,
        "crawled_at": datetime.utcnow().isoformat() + "Z",
    }

    for i, url in enumerate(allowed_urls, 1):
        print(f"[{i}/{len(allowed_urls)}] Fetching {url}")

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()

            # Check size
            if len(resp.content) > max_bytes:
                print(f"  ⊘ Too large ({len(resp.content)} bytes)")
                stats["skipped"] += 1
                continue

            # Extract sections
            sections = extract_text_sections(resp.text, url)

            # Filter by min chars
            valid_sections = []
            for sec in sections:
                combined = sec["heading"] + " " + sec["text"]
                if len(combined) >= min_chars:
                    valid_sections.append(sec)

            if not valid_sections:
                print(f"  ⊘ No valid text sections")
                stats["skipped"] += 1
                continue

            # Create chunks
            doc_id_base = urlparse(url).path.strip("/").replace("/", "_") or "home"
            for j, sec in enumerate(valid_sections):
                chunk = {
                    "doc_id": f"{doc_id_base}_{j}",
                    "url": url,
                    "title": sec["title"],
                    "heading": sec["heading"],
                    "text": sec["text"],
                    "last_fetched": datetime.utcnow().isoformat() + "Z",
                    "tags": _extract_tags(url, sec["heading"]),
                }
                chunks.append(chunk)

            stats["success"] += 1
            stats["total_chunks"] += len(valid_sections)
            print(f"  ✓ Extracted {len(valid_sections)} sections")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            stats["failed"] += 1

        # Rate limiting
        time.sleep(1.0 / rate_limit)

    return chunks, stats


def _extract_tags(url: str, heading: str) -> list[str]:
    """Extract tags from URL and heading."""
    tags = []
    path = urlparse(url).path.lower()

    # URL-based tags
    if "/about" in path or "/our-story" in path:
        tags.append("about")
    if "/leadership" in path or "/team" in path:
        tags.append("leadership")
    if "/services" in path:
        tags.append("services")
    if "/resources" in path:
        tags.append("resources")
    if "/contact" in path:
        tags.append("contact")

    # Heading-based tags
    heading_lower = heading.lower()
    if "leadership" in heading_lower or "team" in heading_lower:
        tags.append("leadership")
    if "about" in heading_lower or "who we are" in heading_lower:
        tags.append("about")
    if "founded" in heading_lower or "history" in heading_lower:
        tags.append("history")

    return list(set(tags)) or ["general"]


def save_output(chunks: list[dict[str, Any]], stats: dict[str, Any]) -> None:
    """Save chunks to JSONL and stats to meta.json."""
    # Save chunks
    with open(OUTPUT_PATH, "w") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"✓ Saved {len(chunks)} chunks to {OUTPUT_PATH}")

    # Save metadata
    with open(META_PATH, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"✓ Saved metadata to {META_PATH}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Site Snapshot Crawler")
    print("=" * 60)

    # Load policy
    policy = load_policy()
    print(f"✓ Loaded policy from {POLICY_PATH}")

    # Crawl
    chunks, stats = crawl(policy)

    # Save
    save_output(chunks, stats)

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total URLs: {stats['total_urls']}")
    print(f"  Success: {stats['success']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Total chunks: {stats['total_chunks']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
