# HanuAI Task 1 — Technical Report
## Best Buy Canada Review Scraping and Sentiment Analysis

### Objective
Collect at least 50 publicly accessible reviews for Sony WH-1000XM5 headphones from Best Buy Canada, structure review metadata, assign sentiment and aspect tags, and translate review patterns into business recommendations.

### Collection workflow
A visible Playwright Chromium session opens the product page. The collector searches rendered DOM for likely review containers, extracts available title/body/date/rating/reviewer fields, generates a stable hash-based identifier where no review ID is exposed, deduplicates records, checkpoints to CSV, and attempts to use normal “Show More” or “Next” controls. The live page may require selector updates. Collection must stop if access controls or CAPTCHA appear.

### Anti-scraping and reliability
- **IP blocking / throttling:** keep request volume low, use modest delays, avoid unnecessary repeated requests, and cache results. Proxies must not be used to evade bans or access restrictions.
- **CAPTCHA / bot detection:** do not bypass CAPTCHA, login walls, or access controls. Stop automated collection and use an authorized export or request permission.
- **Retries:** add bounded retries with exponential backoff for temporary network errors. Do not repeatedly retry permanent access-denied responses.
- **Pagination / sorting:** when permitted, collect pages and sort modes through ordinary site controls; deduplicate records and record the filter used.

### Text processing and sentiment
The analysis script combines review title and body, normalizes whitespace, assigns Positive/Negative/Neutral using a transparent word-lexicon baseline, and adds aspect-sentiment tags for sound, comfort, battery, connectivity, design/build, price/value, reliability, and satisfaction. This baseline is easy to reproduce but is not a fine-tuned transformer. It can miss sarcasm, negation, and mixed sentiment.

### Findings and business recommendations
Populate this section only after running `analyze_reviews.py` on actual collected reviews. Report:
- number of unique reviews and date range;
- rating distribution and positive/negative/neutral counts;
- most frequent aspect tags, split by sentiment;
- examples of recurring positive themes and negative pain points;
- recommendations grounded in observed records.

Do not invent results if fewer than 50 genuine records were collected. A scraped sample is not necessarily representative of every buyer.

### Limitations and future work
Selectors can break as the site changes; dynamic review content may not be exposed to the parser; missing ratings or dates should remain missing; keyword tags and lexicon sentiment require validation against a manually labelled sample. Future improvements include a transformer sentiment model, human-labelled evaluation, aspect extraction using a domain ontology, and collection logs for each sort/filter/page.
