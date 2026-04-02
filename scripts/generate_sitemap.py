#!/usr/bin/env python3
"""Generate sitemap.xml for es.ghostofradio.com"""
import os
from pathlib import Path
from datetime import datetime

SITE_ROOT = Path("/Users/mac1/Projects/ghostofradio-es")
BASE_URL = "https://es.ghostofradio.com"

SKIP_DIRS = {"css", "js", "images", "audio", "blog", "rss", "downloads", "research", "scripts"}

def generate():
    urls = []
    today = datetime.now().strftime("%Y-%m-%d")

    # Static pages (high priority)
    static = [
        ("", "1.0", "daily"),
        ("shows.html", "0.9", "daily"),
        ("about.html", "0.7", "monthly"),
    ]
    for path, priority, freq in static:
        url = f"{BASE_URL}/{path}"
        urls.append((url, today, freq, priority))

    # Show index pages
    for show_dir in sorted(SITE_ROOT.iterdir()):
        if show_dir.is_dir() and show_dir.name not in SKIP_DIRS:
            idx = show_dir / "index.html"
            if idx.exists():
                slug = show_dir.name
                urls.append((f"{BASE_URL}/{slug}/", today, "daily", "0.8"))

    # All episode pages
    for show_dir in sorted(SITE_ROOT.iterdir()):
        if show_dir.is_dir() and show_dir.name not in SKIP_DIRS:
            slug = show_dir.name
            for html in sorted(show_dir.glob("*.html")):
                if html.name == "index.html":
                    continue
                mtime = datetime.fromtimestamp(html.stat().st_mtime).strftime("%Y-%m-%d")
                urls.append((f"{BASE_URL}/{slug}/{html.name}", mtime, "monthly", "0.6"))

    # Build XML
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url, lastmod, freq, priority in urls:
        lines.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""")
    lines.append("</urlset>")

    sitemap = "\n".join(lines)
    out = SITE_ROOT / "sitemap.xml"
    out.write_text(sitemap)
    print(f"✓ Sitemap: {len(urls)} URLs → sitemap.xml")
    return len(urls)

if __name__ == "__main__":
    generate()
