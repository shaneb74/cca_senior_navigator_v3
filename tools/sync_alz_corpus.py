#!/usr/bin/env python3
from __future__ import annotations
import httpx, time, re, json, hashlib
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timezone

ALZ_URLS = [
    "https://www.alz.org/alzheimers-dementia/what-is-alzheimers",
    "https://www.alz.org/alzheimers-dementia/dementia-basics/what-is-dementia",
    "https://www.alz.org/alzheimers-dementia/symptoms",
    "https://www.alz.org/alzheimers-dementia/stages",
    "https://www.alz.org/alzheimers-dementia/diagnosis",
    "https://www.alz.org/alzheimers-dementia/treatments",
    "https://www.alz.org/alzheimers-dementia/what-is-dementia/difference-between-dementia-and-alzheimer-s",
    "https://www.alz.org/alzheimers-dementia/research_progress",
    "https://www.alz.org/alzheimers-dementia/helping-you/alzheimers-and-dementia-resources",
    "https://www.alz.org/help-support/caregiving",
    "https://www.alz.org/help-support/caregiving/care-options",
    "https://www.alz.org/help-support/caregiving/safety",
    "https://www.alz.org/help-support/caregiving/care-options/memory-care",
    "https://www.alz.org/help-support/caregiving/care-options/assisted-living-nursing-homes",
    "https://www.alz.org/help-support/caregiving/daily-care/behaviors",
    "https://www.alz.org/help-support/caregiving/financial-legal-planning",
]

OUT_PATH = Path("config/corp_knowledge.jsonl")
MAX_CHARS = 1400
OVERLAP = 150
UA = "cca-senior-navigator/1.0 (+https://conciergecareadvisors.com)"

def slugify(s: str) -> str:
    s = re.sub(r"\s+", "-", s.strip().lower())
    s = re.sub(r"[^a-z0-9\-]+", "", s)
    return s[:80] or "section"

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fetch(url: str) -> tuple[str, str, str]:
    with httpx.Client(timeout=20.0, follow_redirects=True, headers={"User-Agent": UA}) as client:
        r = client.get(url)
        r.raise_for_status()
        html = r.text
    soup = BeautifulSoup(html, "html.parser")

    title = (soup.title.text.strip() if soup.title else url)
    # try updated time in <time> or meta; else now
    updated = ""
    time_el = soup.find("time", {"datetime": True}) or soup.find("meta", {"property":"article:modified_time"}) or soup.find("meta", {"name":"last-modified"})
    if time_el:
        updated = time_el.get("datetime") or time_el.get("content", "")
    updated_at = updated or now_iso()

    main = soup.find("main") or soup.find(attrs={"role": "main"}) or soup.find("article") or soup.body
    if not main:
        return title, updated_at, ""

    # remove non-content sections
    for bad in main.select("nav, footer, aside, script, style"):
        bad.decompose()

    parts = []
    for el in main.find_all(["h1","h2","h3","h4","p","li","ul","ol","strong","em","a"], recursive=True):
        if el.name in ("h1","h2","h3","h4"):
            lvl = int(el.name[1])
            parts.append(f"\n\n{('#'*lvl)} {el.get_text(strip=True)}\n")
        elif el.name == "li":
            parts.append(f"- {el.get_text(' ', strip=True)}")
        elif el.name == "a":
            href = el.get("href") or ""
            txt = el.get_text(strip=True)
            if href and href.startswith("http"):
                parts.append(f"[{txt}]({href})")
            else:
                parts.append(txt)
        else:
            parts.append(el.get_text(" ", strip=True))

    md = "\n".join(p for p in parts if p and p.strip())
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return title, updated_at, md

def chunk_text(md: str, title: str, url: str, updated_at: str) -> list[dict]:
    blocks = re.split(r"\n(?=#{1,4}\s)", md) if md else []
    chunks = []
    for block in blocks or [md]:
        b = block.strip()
        if not b:
            continue
        i = 0
        while i < len(b):
            j = min(len(b), i + MAX_CHARS)
            k = b.rfind(". ", i, j)
            if k == -1 or k < i + MAX_CHARS - 300:
                k = j
            piece = b[i:k].strip()
            i = max(k - OVERLAP, k)
            if len(piece) < 100:
                continue
            m = re.match(r"^#{1,4}\s+(.+)", piece)
            section = slugify(m.group(1)) if m else slugify(title)
            h = hashlib.sha1((url + section + piece[:80]).encode()).hexdigest()[:12]
            chunks.append({
                "id": f"alz::{h}",
                "title": title,
                "section": section,
                "text": piece,
                "url": url,
                "updated_at": updated_at,
                "source": "alz.org"
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
    add = 0
    with path.open("a", encoding="utf-8") as f:
        for it in items:
            if it["id"] in existing:
                continue
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
            add += 1
    print(f"[ALZ_SYNC] appended {add} new chunks to {path}")

def main():
    total = 0
    for url in ALZ_URLS:
        print(f"[ALZ_SYNC] fetching: {url}")
        try:
            title, updated_at, md = fetch(url)
            if not md:
                print(f"[ALZ_SYNC] WARNING empty content for {url}")
                continue
            ch = chunk_text(md, title, url, updated_at)
            append_jsonl(OUT_PATH, ch)
            total += len(ch)
            time.sleep(0.5)
        except Exception as e:
            print(f"[ALZ_SYNC] ERROR fetching {url}: {e}")
            continue
    print(f"[ALZ_SYNC] DONE; total chunks added ~ {total}")

if __name__ == "__main__":
    main()
