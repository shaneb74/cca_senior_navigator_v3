#!/usr/bin/env python3
from __future__ import annotations
import httpx, time, re, json, hashlib
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timezone

VA_URLS = [
    "https://www.va.gov/pension/aid-attendance-housebound/",
    "https://www.va.gov/pension/eligibility/",
    "https://www.va.gov/family-member-benefits/",
    "https://www.caregiver.va.gov/",
]

OUT_PATH = Path("config/corp_knowledge.jsonl")
MAX_CHARS = 1400          # chunk size
OVERLAP = 150             # chunk overlap (soft)
UA = "cca-senior-navigator/1.0 (+https://conciergecareadvisors.com)"

def slugify(s: str) -> str:
    s = re.sub(r"\s+", "-", s.strip().lower())
    s = re.sub(r"[^a-z0-9\-]+", "", s)
    return s[:80] or "section"

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fetch(url: str) -> tuple[str, str, str]:
    """Return (title, updated_at, markdown_text)."""
    with httpx.Client(timeout=20.0, headers={"User-Agent": UA}) as client:
        r = client.get(url, follow_redirects=True)
        r.raise_for_status()
        html = r.text

    soup = BeautifulSoup(html, "html.parser")

    # title
    title_el = soup.find("title")
    title = (title_el.text or url).strip() if title_el else url

    # updated at (try microdata/date; fallback to today)
    updated = ""
    # Try <time datetime="..."> or meta
    time_el = soup.find("time", {"datetime": True}) or soup.find("meta", {"property":"article:modified_time"}) or soup.find("meta", {"name":"last-modified"})
    if time_el:
        updated = time_el.get("datetime") or time_el.get("content", "")
    updated_at = updated or now_iso()

    # main content (heuristic)
    # prefer role=main or .main or article
    main = soup.find(attrs={"role": "main"}) or soup.find("main") or soup.find("article") or soup.body
    text_parts = []
    if main:
        # strip nav/footer/aside
        for bad in main.select("nav, footer, aside, script, style"):
            bad.decompose()
        # preserve headings + paragraphs
        for el in main.find_all(["h1","h2","h3","h4","p","li","ul","ol","strong","em","a"], recursive=True):
            if el.name in ("h1","h2","h3","h4"):
                text_parts.append(f"\n\n{('#'*(int(el.name[1])))} {el.get_text(strip=True)}\n")
            elif el.name in ("ul","ol"):
                # keep bullets
                pass
            elif el.name == "li":
                text_parts.append(f"- {el.get_text(' ', strip=True)}")
            elif el.name == "a":
                # inline link [text](href)
                href = el.get("href") or ""
                txt = el.get_text(strip=True)
                if href and href.startswith("http"):
                    text_parts.append(f"[{txt}]({href})")
                else:
                    text_parts.append(txt)
            else:
                text_parts.append(el.get_text(" ", strip=True))
    md = "\n".join(p for p in text_parts if p and p.strip())
    # collapse whitespace
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return title, updated_at, md

def chunk_text(md: str, title: str, url: str, updated_at: str) -> list[dict]:
    """Return JSONL-ready chunks with metadata."""
    # split on big headings, then size-bound
    blocks = re.split(r"\n(?=#{1,4}\s)", md) if md else []
    chunks = []
    for block in blocks or [md]:
        b = block.strip()
        if not b:
            continue
        # soft-size chunking
        i = 0
        while i < len(b):
            j = min(len(b), i + MAX_CHARS)
            # try to cut on sentence
            k = b.rfind(". ", i, j)
            if k == -1 or k < i + MAX_CHARS - 300:
                k = j
            piece = b[i:k].strip()
            i = max(k - OVERLAP, k)  # overlap on next
            if len(piece) < 100:
                continue
            # section name from top heading in piece
            m = re.match(r"^#{1,4}\s+(.+)", piece)
            section = slugify(m.group(1)) if m else slugify(title)
            # stable id: hash(url + section + first 80 chars)
            h = hashlib.sha1((url + section + piece[:80]).encode()).hexdigest()[:12]
            chunks.append({
                "id": f"va::{h}",
                "title": title,
                "section": section,
                "text": piece,
                "url": url,
                "updated_at": updated_at,
                "source": "va.gov"
            })
    return chunks

def append_jsonl(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = set()
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    j = json.loads(line)
                    existing.add(j.get("id"))
                except Exception:
                    pass
    # append deduped
    with path.open("a", encoding="utf-8") as f:
        add = 0
        for it in items:
            if it["id"] in existing:
                continue
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
            add += 1
    print(f"[VA_SYNC] appended {add} new chunks to {path}")

def main():
    total = 0
    for url in VA_URLS:
        print(f"[VA_SYNC] fetching: {url}")
        try:
            title, updated_at, md = fetch(url)
            if not md:
                print(f"[VA_SYNC] WARNING empty content for {url}")
                continue
            ch = chunk_text(md, title, url, updated_at)
            append_jsonl(OUT_PATH, ch)
            total += len(ch)
            time.sleep(0.5)  # be polite
        except Exception as e:
            print(f"[VA_SYNC] ERROR fetching {url}: {e}")
            continue
    print(f"[VA_SYNC] DONE; total chunks added ~ {total}")

if __name__ == "__main__":
    main()
