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
import xml.etree.ElementTree as ET
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
    """Fetch sitemap.xml and extract URLs. Try multiple sitemap locations."""
    sitemap_candidates = ["/sitemap.xml", "/sitemap_index.xml"]
    headers = {"User-Agent": "CCA-SnapshotBot/1.0 (+https://www.conciergecareadvisors.com)"}
    
    for sitemap_path in sitemap_candidates:
        sitemap_url = urljoin(root, sitemap_path)
        try:
            print(f"  Trying {sitemap_url}...")
            resp = requests.get(sitemap_url, timeout=10, headers=headers)
            resp.raise_for_status()
            
            # Parse with xml.etree
            root_elem = ET.fromstring(resp.content)
            
            # Get namespace (usually {http://www.sitemaps.org/schemas/sitemap/0.9})
            namespace = root_elem.tag.split('}')[0].strip('{') if '}' in root_elem.tag else ''
            ns = {'ns': namespace} if namespace else {}
            
            # Look for <url><loc> (regular sitemap)
            urls = []
            if ns:
                urls = [loc.text for loc in root_elem.findall('.//ns:url/ns:loc', ns) if loc.text]
            else:
                urls = [loc.text for loc in root_elem.findall('.//url/loc') if loc.text]
            
            if urls:
                print(f"✓ Loaded {len(urls)} URLs from {sitemap_path}")
                return urls
            
            # Look for <sitemap><loc> (sitemap index)
            sitemap_locs = []
            if ns:
                sitemap_locs = [loc.text for loc in root_elem.findall('.//ns:sitemap/ns:loc', ns) if loc.text]
            else:
                sitemap_locs = [loc.text for loc in root_elem.findall('.//sitemap/loc') if loc.text]
            
            if sitemap_locs:
                print(f"✓ Found {len(sitemap_locs)} child sitemaps in {sitemap_path}")
                all_urls = []
                for child_sitemap in sitemap_locs[:10]:  # Limit to 10 child sitemaps
                    try:
                        print(f"    Fetching child sitemap: {child_sitemap}")
                        child_resp = requests.get(child_sitemap, timeout=10, headers=headers)
                        child_resp.raise_for_status()
                        child_root = ET.fromstring(child_resp.content)
                        
                        if ns:
                            child_urls = [loc.text for loc in child_root.findall('.//ns:url/ns:loc', ns) if loc.text]
                        else:
                            child_urls = [loc.text for loc in child_root.findall('.//url/loc') if loc.text]
                        
                        all_urls.extend(child_urls)
                        print(f"      ✓ Got {len(child_urls)} URLs")
                    except Exception as child_e:
                        print(f"      ⚠ Child sitemap failed: {child_e}")
                
                if all_urls:
                    print(f"✓ Total {len(all_urls)} URLs from child sitemaps")
                    return all_urls
                    
        except Exception as e:
            print(f"  ⚠ {sitemap_path} failed: {e}")
    
    print("⚠ All sitemap attempts failed, will use fallback BFS")
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


def bfs_fallback(root: str, policy: dict[str, Any], robots: RobotFileParser | None) -> list[str]:
    """Fallback BFS crawl from root if sitemap fails."""
    print("⚠ Starting BFS fallback from root URL")
    headers = {"User-Agent": "CCA-SnapshotBot/1.0 (+https://www.conciergecareadvisors.com)"}
    
    allow = policy.get("allow", [])
    exclude = policy.get("exclude", [])
    max_pages = policy.get("max_pages", 200)
    max_depth = policy.get("max_depth", 3)
    
    visited = set()
    queue = [(root, 0)]  # (url, depth)
    discovered_urls = []
    
    while queue and len(discovered_urls) < max_pages:
        url, depth = queue.pop(0)
        
        if url in visited or depth > max_depth:
            continue
        
        visited.add(url)
        
        # Check filters
        if exclude and matches_pattern(url, exclude):
            continue
        if allow and not matches_pattern(url, allow):
            continue
        if robots and not robots.can_fetch("*", url):
            continue
        
        discovered_urls.append(url)
        print(f"  BFS discovered [{len(discovered_urls)}]: {url} (depth={depth})")
        
        # Fetch and extract links
        try:
            resp = requests.get(url, timeout=10, headers=headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            
            for link in soup.find_all("a", href=True):
                next_url = urljoin(url, link["href"])
                
                # Keep same domain
                if urlparse(next_url).netloc != urlparse(root).netloc:
                    continue
                
                # Remove fragments
                next_url = next_url.split("#")[0]
                
                if next_url not in visited:
                    queue.append((next_url, depth + 1))
        
        except Exception as e:
            print(f"    ⚠ BFS fetch failed: {e}")
        
        # Rate limit
        time.sleep(0.5)
    
    print(f"✓ BFS discovered {len(discovered_urls)} URLs")
    return discovered_urls


# ==============================================================================
# HYGIENE FILTERS (Stage 3.6)
# ==============================================================================
BAD_HEADING_RE = re.compile(
    r"(?i)^(related|recent|tags?|categories|share|disclaimer|copyright|privacy|"
    r"terms|subscribe|newsletter|comments?|posted by|filed under|read more)",
)
BAD_TEXT_RE = re.compile(
    r"(?i)^(related|recent|tags?|categories|back to top|next post|previous|"
    r"comments?|share this|follow us|subscribe|posted in)",
)


def is_boilerplate(heading: str, text: str) -> bool:
    """Check if section looks like boilerplate (navigation, footer, etc)."""
    if BAD_HEADING_RE.search(heading or ""):
        return True
    if BAD_TEXT_RE.search(text or ""):
        return True
    # Detect site nav repetition (same words repeated many times)
    words = text.lower().split()
    if len(words) > 10:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.3:  # Less than 30% unique words
            return True
    return False


def normalize_text(text: str) -> str:
    """Normalize text: collapse spaces, convert bullets to plain sentences."""
    # Collapse multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    # Convert bullet characters to plain text
    text = text.replace('•', '').replace('–', '-').replace('—', '-')
    return text.strip()


def split_long_text(text: str, max_len: int = 1800) -> list[str]:
    """Split text by paragraph boundaries if longer than max_len."""
    if len(text) <= max_len:
        return [text]
    
    # Split by double newlines (paragraphs)
    paragraphs = text.split('\n\n')
    chunks = []
    current = []
    current_len = 0
    
    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > max_len and current:
            # Save current chunk
            chunks.append('\n\n'.join(current))
            current = [para]
            current_len = para_len
        else:
            current.append(para)
            current_len += para_len
    
    if current:
        chunks.append('\n\n'.join(current))
    
    return chunks


def get_content_type(url: str) -> str:
    """Determine content type from URL for weighted retrieval."""
    url_lower = url.lower()
    if "/about" in url_lower or "/our-story" in url_lower:
        return "about"
    if "/leadership" in url_lower or "/team" in url_lower or "/advisory-board" in url_lower:
        return "leadership"
    if "/services" in url_lower or "/senior" in url_lower or "/service/" in url_lower:
        return "services"
    return "blog"


def extract_text_sections(html: str, url: str) -> list[dict[str, Any]]:
    """Extract text sections split by headings (h1-h3) with hygiene filters."""
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
                text = normalize_text(text)
                
                # Apply hygiene filters
                if len(text) >= 200 and not is_boilerplate(current_heading or "", text):
                    # Split if too long
                    text_chunks = split_long_text(text, max_len=1800)
                    for chunk_text in text_chunks:
                        sections.append({
                            "heading": current_heading or page_title,
                            "text": chunk_text,
                        })
            # Start new section
            current_heading = elem.get_text(strip=True)
            current_text = []
        elif elem.name == "p" and elem.string:
            current_text.append(elem.get_text(strip=True))

    # Save final section
    if current_text:
        text = " ".join(current_text).strip()
        text = normalize_text(text)
        
        if len(text) >= 200 and not is_boilerplate(current_heading or "", text):
            text_chunks = split_long_text(text, max_len=1800)
            for chunk_text in text_chunks:
                sections.append({
                    "heading": current_heading or page_title,
                    "text": chunk_text,
                })

    # Add content type to each section
    ctype = get_content_type(url)
    
    return [
        {
            "title": page_title,
            "heading": sec["heading"],
            "text": sec["text"],
            "type": ctype,
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
    
    headers = {"User-Agent": "CCA-SnapshotBot/1.0 (+https://www.conciergecareadvisors.com)"}

    # Load robots.txt
    robots = check_robots(root) if respect_robots else None

    # Collect URLs
    candidate_urls = []
    if use_sitemap:
        candidate_urls = fetch_sitemap(root)
    
    # Fallback to BFS if sitemap failed
    if not candidate_urls:
        candidate_urls = bfs_fallback(root, policy, robots)
    
    if not candidate_urls:
        print("✗ No URLs discovered - check your allow patterns or site availability")
        return [], {
            "total_urls": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "total_chunks": 0,
            "crawled_at": datetime.utcnow().isoformat() + "Z",
        }

    # Filter URLs (already done in BFS, but sitemap URLs need filtering)
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
            resp = requests.get(url, timeout=10, headers=headers)
            resp.raise_for_status()

            # Check size
            if len(resp.content) > max_bytes:
                print(f"  ⊘ Too large ({len(resp.content)} bytes)")
                stats["skipped"] += 1
                continue

            # Extract sections (now includes type and hygiene filtering)
            sections = extract_text_sections(resp.text, url)

            # Sections are already filtered by hygiene rules (200-1800 chars)
            # Just need to check min_chars policy (though hygiene already enforces 200 minimum)
            valid_sections = []
            for sec in sections:
                combined = sec["heading"] + " " + sec["text"]
                # Note: min_chars from policy, but hygiene already enforces >= 200
                if len(combined) >= max(200, min_chars):
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
                    "type": sec["type"],  # about, leadership, services, or blog
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
    """Save chunks to JSONL and stats to meta.json with versioning."""
    # Save chunks
    with open(OUTPUT_PATH, "w") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"✓ Saved {len(chunks)} chunks to {OUTPUT_PATH}")

    # Add version for cache busting
    stats["version"] = int(time.time())
    
    # Save metadata
    with open(META_PATH, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"✓ Saved metadata to {META_PATH} (version: {stats['version']})")


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
