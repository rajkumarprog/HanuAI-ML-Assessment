HanuAI Task 1 — working local workflow
========================================

This is a new final working package for Task 1. It does not overwrite your previous package.

Files:
- collect_bestbuy_reviews.py — opens Best Buy Canada in a visible Chromium browser, attempts to parse review cards, checkpoints real records to CSV, and stops when no next/show-more control is found.
- analyze_reviews.py — cleans real collected reviews, applies a transparent lexicon sentiment baseline and keyword aspect tags, and exports the analyzed dataset.
- requirements.txt — dependencies.

Setup in VS Code terminal:
    py -m venv .venv
    .venv\Scripts\activate
    python -m pip install -r requirements.txt
    playwright install chromium

Run:
    python collect_bestbuy_reviews.py
    python analyze_reviews.py

Expected files:
    data/bestbuy_reviews_raw.csv
    data/bestbuy_reviews_with_sentiment.csv

IMPORTANT:
- The scraper's selectors are best-effort and may need updating to match Best Buy's live DOM.
- Do not bypass CAPTCHA, login walls, rate limits, or other access restrictions.
- The collector may stop with fewer than 50 rows if the page doesn't expose review cards or pagination in a parseable way. Inspect the page/DOM or use a permitted export. Do not fabricate records.
- Sentiment and aspect tags are a baseline heuristic, not a fine-tuned model. Mention this limitation in the report.
- The dataset is only complete after the local run successfully creates at least 50 genuine unique review rows.
