"""
HanuAI Task 1 — Best Buy Canada review collector
Run locally on your own computer with a normal browser session.
This script does not bypass CAPTCHA, login walls, rate limits, or other access controls.
Inspect the rendered page and adjust selectors if Best Buy changes its markup.
"""
import csv
import hashlib
import re
import time
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

PRODUCT_URL = "https://www.bestbuy.ca/en-ca/product/sony-wh-1000xm5-over-ear-noise-cancelling-bluetooth-headphones-black/16162187"
OUT = Path("data")
OUT.mkdir(exist_ok=True)
RAW_CSV = OUT / "bestbuy_reviews_raw.csv"
SOURCE = "Best Buy Canada"

def text_of(node, selectors):
    for selector in selectors:
        el = node.query_selector(selector)
        if el:
            text = " ".join((el.inner_text() or "").split())
            if text:
                return text
    return ""

def rating_from(text):
    m = re.search(r'([1-5](?:\.\d+)?)\s*(?:out of 5|/5|stars?)', text, re.I)
    if m:
        try:
            value = float(m.group(1))
            return value if 1 <= value <= 5 else None
        except ValueError:
            pass
    return None

def parse_date(text):
    text = (text or "").strip()
    for fmt in ("%Y-%m-%d", "%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    m = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b', text, re.I)
    if m:
        for fmt in ("%b %d, %Y", "%B %d, %Y", "%b %d %Y", "%B %d %Y"):
            try:
                return datetime.strptime(m.group(0).replace(",", ""), fmt.replace(",", "")).strftime("%Y-%m-%d")
            except ValueError:
                pass
    return ""

def review_container_candidates(page):
    # Broad, inspectable selectors because retail sites frequently update CSS classes.
    selectors = [
    '[data-testid*="review"]',
    '[class*="review-item"]',
    '[class*="reviewItem"]',
    '[class*="review-content"]',
    '[class*="review"]',
    'article'
]
    found = []
    seen = set()
    for sel in selectors:
        try:
            loc = page.locator(sel)
            count = min(loc.count(), 300)
            for i in range(count):
                node = loc.nth(i)
                try:
                    body = (node.inner_text(timeout=1500) or "").strip()
                except Exception:
                    continue
                if len(body) < 40:
                    continue
                # Deduplicate same DOM node/text found through different selectors.
                key = hashlib.sha1(body.encode("utf-8", "ignore")).hexdigest()
                if key not in seen:
                    seen.add(key)
                    found.append((node, body))
        except Exception:
            continue
    return found

def parse_current_page(page):
    records = []
    for node, full_text in review_container_candidates(page):
        title = text_of(node, [
            '[data-testid*="title"]', '[class*="title"]', 'h3', 'h4'
        ])
        body = text_of(node, [
            '[data-testid*="text"]', '[class*="comment"]',
            '[class*="content"]', '[class*="body"]', 'p'
        ])
        reviewer = text_of(node, [
            '[class*="author"]', '[class*="reviewer"]',
            '[data-testid*="author"]'
        ])
        date_text = text_of(node, ['time', '[class*="date"]'])
        rating_text = ""
        try:
            rating_el = node.query_selector('[aria-label*="star"], [aria-label*="out of 5"], [class*="rating"]')
            if rating_el:
                rating_text = (rating_el.get_attribute("aria-label") or "") + " " + (rating_el.inner_text() or "")
        except Exception:
            pass
        rating = rating_from(rating_text + " " + full_text[:250])
        if not body:
            # If the page gives one review block without a dedicated body selector,
            # use the block text after removing title/reviewer/date fragments.
            body = full_text
        if len(body.strip()) < 15:
            continue
        review_date = parse_date(date_text)
        stable = "|".join([title, body, review_date, reviewer, str(rating)])
        rid = hashlib.sha256(stable.encode("utf-8", "ignore")).hexdigest()[:20]
        records.append({
            "review_id": rid,
            "review_title": title,
            "review_body": body,
            "review_date": review_date,
            "star_rating": rating,
            "source_platform": SOURCE,
            "reviewer_name": reviewer,
            "product_url": PRODUCT_URL,
            "collection_page_url": page.url,
            "collection_timestamp_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        })
    # In-page de-duplication
    unique = {}
    for row in records:
        unique[row["review_id"]] = row
    return list(unique.values())

def click_next_or_more(page):
    candidates = [
        'button:has-text("Show More")',
        'button:has-text("Load More")',
        'button:has-text("Next")',
        'a:has-text("Next")',
        '[aria-label*="Next"]',
        'button[aria-label*="next"]'
    ]
    for selector in candidates:
        try:
            loc = page.locator(selector).first
            if loc.count() and loc.is_visible() and loc.is_enabled():
                loc.click(timeout=3000)
                page.wait_for_timeout(1800)
                return True
        except Exception:
            pass
    return False

def main():
    all_rows = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(locale="en-CA")
        page.set_default_timeout(7000)
        print("Opening Best Buy Canada product page.")
        page.goto(PRODUCT_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3500)
        print("If a consent banner appears, handle it manually in the browser.")
        print("Do not bypass CAPTCHA or access restrictions. If a challenge appears, stop and use an approved export.")
        input("When the product page is visible and loaded, press Enter here to begin parsing: ")
        # Try to move to review section
        for label in ["Customer Reviews", "Reviews"]:
            try:
                loc = page.get_by_text(label, exact=False).first
                if loc.count():
                    loc.scroll_into_view_if_needed(timeout=3000)
                    break
            except Exception:
                pass
        page.wait_for_timeout(1500)

        max_pages = 30
        for page_num in range(1, max_pages + 1):
            rows = parse_current_page(page)
            before = len(all_rows)
            for row in rows:
                all_rows[row["review_id"]] = row
            print(f"Page pass {page_num}: parsed {len(rows)} candidate records; unique total {len(all_rows)}")
            # Save checkpoint after every pass
            if all_rows:
                with RAW_CSV.open("w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=list(next(iter(all_rows.values())).keys()))
                    writer.writeheader()
                    writer.writerows(all_rows.values())
            if len(all_rows) >= 50:
                print("Reached the assignment minimum of 50 unique records.")
                break
            if len(all_rows) == before and page_num >= 2:
                print("No new records detected on this pass.")
            if not click_next_or_more(page):
                print("No supported next/show-more control detected. Stopping rather than guessing or bypassing restrictions.")
                break
            time.sleep(1.5)  # conservative pacing

        browser.close()

    print(f"Saved {len(all_rows)} unique records to {RAW_CSV.resolve()}")
    if len(all_rows) < 50:
        print("WARNING: fewer than 50 records were collected. Inspect the site DOM and update selectors or use an authorized export.")
        print("Do not claim the assignment's 50-review minimum is met until the CSV contains at least 50 genuine records.")
    else:
        print("Collection minimum met. Next run analyze_reviews.py.")

if __name__ == "__main__":
    main()
