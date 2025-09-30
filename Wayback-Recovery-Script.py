#!/usr/bin/env python3
"""
Wayback-Recovery-Script.py

Primary Goal: Extract ALL structured metadata from every item in an archived catalogue.
Secondary Goal: Download all related media (video/image/audio) when possible, using yt-dlp.

This script is designed to work with archived catalogues (like AtoM) on the Wayback Machine.
"""
import requests
import os
import json
import subprocess
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- Configuration Constants (EDIT THESE PLACEHOLDERS) ---
# Full Wayback URL of the archived collection's root (including timestamp)
WAYBACK_ROOT = "https://web.archive.org/web/YYYYMMDDHHMMSS/http://original.archive.org/"
# The URL path to the browsable index of items within the archive.
BROWSE_PATH = "informationobject/browse?view=card&onlyMedia=1&topLod=0" 
BROWSE_URL = urljoin(WAYBACK_ROOT, BROWSE_PATH)
# Output directory for metadata and files
OUT_DIR = "recovered_archive_data" 
YT_DLP_BIN = "yt-dlp"

# --- Processing Parameters ---
MAX_ITEMS_TO_PROCESS = 1000 # Set a reasonable limit, or None for all
SLEEP_BETWEEN = 2.0         # Respectful delay between item requests

# --- Setup ---
os.makedirs(OUT_DIR, exist_ok=True)
session = requests.Session()
# Use a polite, professional User-Agent string
session.headers.update(
    {
        "User-Agent": "Digital-Archaeology-Harvester/1.0 (Contact: preservation_research@example.org)"
    }
)


# ------------------ Utility Functions ------------------ #

def fetch(url):
    """Fetch the content of a given URL."""
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def find_item_links(html):
    """Extract unique item links from the browse page, generalising the URL filtering."""
    soup = BeautifulSoup(html, "lxml")
    links = []
    
    # Placeholder domain part of the URL structure to check against
    ARCHIVED_DOMAIN_CHECK = re.search(r"https?://(.*?)/", WAYBACK_ROOT).group(1) if re.search(r"https?://(.*?)/", WAYBACK_ROOT) else "original.archive.org"

    for a in soup.select("a[href]"):
        href = a["href"]
        # Skip navigation links common in these platforms
        if "informationobject/browse" in href or "search/advanced" in href:
            continue
            
        # Ensure the link points to an item within the archived collection structure
        if ARCHIVED_DOMAIN_CHECK in href or href.startswith("/"):
            # Construct the full Wayback URL for the item
            full = urljoin("https://web.archive.org", href)
            
            # Final check to ensure we are only collecting links relevant to the archived domain
            if ARCHIVED_DOMAIN_CHECK in full:
                links.append(full)
    return sorted(set(links))


def safe_name(s):
    """Make a string safe for use as a directory name."""
    return "".join(c if c.isalnum() or c in " ._-()" else "_" for c in s)[:80]


def download_with_ytdlp(url, outdir, counter=None):
    """Download media using yt-dlp, performing Wayback URL cleansing."""
    target_url = url
    if url.startswith("https://web.archive.org/web/"):
        # CRITICAL: Strip the Wayback prefix (e.g., /web/YYYYMMDDHHMMSS/)
        match = re.search(r"/(https?://.*)", url)
        if match:
            target_url = match.group(1)

    # Output filename template for yt-dlp
    if counter is not None:
        outtmpl = os.path.join(outdir, f"%(title)s_{counter}.%(ext)s")
    else:
        outtmpl = os.path.join(outdir, "%(title)s.%(ext)s")

    cmd = [YT_DLP_BIN, "-o", outtmpl, target_url, "--no-overwrites"]
    print("    Running download:", " ".join(cmd[:3]) + "...")
    subprocess.run(cmd, check=True)


# ------------------ Metadata Extraction ------------------ #

def extract_item_metadata(html, page_url):
    """
    Extracts structured descriptive metadata and media links using a dual-strategy 
    and attempts to preserve section hierarchy.
    """
    soup = BeautifulSoup(html, "lxml")

    meta = {
        "url": page_url,
        "title": (soup.title.string or "").strip(),
        "descriptive_metadata": {},
        "internet_archive": [],
        "media_urls": [],
    }

    # 1. Scope: Try to find main metadata content column
    main_content = (
        soup.find("div", id="main-column")
        or soup.find("div", id="content-main")
        or soup.find("div", class_="content")
        or soup
    )

    # 2. Extract section-based metadata
    for header in main_content.find_all(["h2", "h3"]):
        section_title = header.get_text(strip=True)
        if not section_title or "Search" in section_title or "Browse" in section_title:
            continue

        section_data = {}
        section_nodes = []

        # Collect siblings until next header of same level
        for sib in header.find_all_next():
            if sib.name in ["h2", "h3"]:
                break
            section_nodes.append(sib)

        # Strategy A: Parse dl/dt/dd pairs (Robustness Fallback)
        for dl in [s for s in section_nodes if s.name == "dl"]:
            for dt, dd in zip(dl.find_all("dt"), dl.find_all("dd")):
                key = dt.get_text(strip=True).replace(":", "")
                value = dd.get_text(" ", strip=True)
                if key and value:
                    section_data[key] = value

        # Strategy B: Parse <p> or <div> fields with <strong> labels (Precision)
        for field in [s for s in section_nodes if s.name in ["p", "div", "li"]]:
            label_tag = field.find("strong")
            if label_tag:
                key = label_tag.get_text(strip=True).replace(":", "")
                # Create a copy of the tag before extraction for cleaner text handling
                temp_field = BeautifulSoup(str(field), "lxml")
                # Find and remove the strong tag from the temporary copy
                temp_field.find('strong').extract()
                value = temp_field.get_text(" ", strip=True)
                if key and value:
                    section_data[key] = value

        if section_data:
            meta["descriptive_metadata"][section_title] = section_data

    # 3. Extract media and archive links
    IGNORE_URL_PARTS = [
        "docs.accesstomemory.org",
        "/downloads/exports/",
        "facebook.com",
        "twitter.com",
    ]

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(part in href for part in IGNORE_URL_PARTS):
            continue

        # Internet Archive links (as potential download targets)
        if "archive.org" in href:
            if "/web/" in href and (href.endswith("/") or "index.html" in href):
                continue
            if href.lower().endswith((".xml", ".pdf", ".txt")):
                continue
            meta["internet_archive"].append(href)

        # Direct media files
        if href.lower().endswith(
            (".mp4", ".mkv", ".webm", ".ogg", ".mov", ".jpg", ".png", ".gif")
        ):
            meta["media_urls"].append(urljoin(page_url, href))

    # Video <source> tags
    for v in soup.find_all("video"):
        if v.get("src"):
            meta["media_urls"].append(urljoin(page_url, v["src"]))
        for s in v.find_all("source"):
            if s.get("src"):
                meta["media_urls"].append(urljoin(page_url, s["src"]))

    meta["internet_archive"] = list(set(meta["internet_archive"]))
    meta["media_urls"] = list(set(meta["media_urls"]))

    return meta


# ------------------ Main Execution ------------------ #

def main():
    """Main execution function to scrape metadata and media."""
    print("Fetching browse page...")
    try:
        browse_html = fetch(BROWSE_URL)
        item_links = find_item_links(browse_html)[:MAX_ITEMS_TO_PROCESS]
    except Exception as e:
        print(f"Failed to fetch browse page or find links: {e}")
        return

    print(f"Total items scheduled for processing: {len(item_links)}")

    for i, link in enumerate(item_links, 1):
        print(f"\n[{i}/{len(item_links)}] Processing: {link}")

        try:
            html = fetch(link)
            meta = extract_item_metadata(html, link)

            # Save metadata JSON
            dirname = os.path.join(
                OUT_DIR, safe_name(meta["title"] or f"item_{i}")
            )
            os.makedirs(dirname, exist_ok=True)

            metadata_path = os.path.join(dirname, "metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            print(f"    ✓ Metadata saved to {metadata_path}")

            # Download ALL media (videos + images)
            all_media = meta["media_urls"] + meta["internet_archive"]
            if all_media:
                print(
                    f"    [Download Check] {len(all_media)} media link(s) found. Attempting downloads..."
                )
                for idx, murl in enumerate(all_media, 1):
                    try:
                        download_with_ytdlp(
                            murl, dirname, counter=idx if len(all_media) > 1 else None
                        )
                        print(f"    ✓ Downloaded media {idx}/{len(all_media)}")
                    except subprocess.CalledProcessError as e:
                        print(
                            f"    ✗ Download failed (yt-dlp error code {e.returncode} for {murl})."
                        )
                    except Exception as e:
                        print(f"    ✗ Download failed (other error: {e}).")
            else:
                print("    ✗ No suitable media or Internet Archive link found.")

        except Exception as e:
            print(f"Error processing item {link}: {e}")

        time.sleep(SLEEP_BETWEEN)


if __name__ == "__main__":
    main()
