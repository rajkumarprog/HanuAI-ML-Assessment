
import json
import re
from pathlib import Path

import pandas as pd

html_path = Path(r"D:\HanuAI\bestbuy_reviews.html")
output_path = Path("data") / "bestbuy_reviews_raw.csv"

html = html_path.read_text(encoding="utf-8", errors="ignore")

# Find the embedded customerReviews array and decode complete JSON objects.
marker = '"customerReviews":['
start = html.find(marker)

if start == -1:
    marker = '"customerReviews": ['
    start = html.find(marker)

if start == -1:
    raise SystemExit(
        "Could not find the customerReviews array in the saved HTML."
    )

start += len(marker)

# Walk the JSON array, respecting quoted strings and escaped characters.
objects = []
depth = 0
object_start = None
in_string = False
escaped = False

for i in range(start, len(html)):
    ch = html[i]

    if in_string:
        if escaped:
            escaped = False
        elif ch == "\\":
            escaped = True
        elif ch == '"':
            in_string = False
        continue

    if ch == '"':
        in_string = True
    elif ch == "{":
        if depth == 0:
            object_start = i
        depth += 1
    elif ch == "}":
        depth -= 1
        if depth == 0 and object_start is not None:
            objects.append(html[object_start:i + 1])
            object_start = None
    elif ch == "]" and depth == 0:
        break

records = []
seen_ids = set()

for raw in objects:
    try:
        item = json.loads(raw)
    except json.JSONDecodeError:
        continue

    review_id = str(item.get("id", "")).strip()
    title = str(item.get("title", "")).strip()
    body = str(item.get("comment", "")).strip()
    rating = item.get("rating")

    if not review_id or not body or rating is None:
        continue

    if review_id in seen_ids:
        continue
    seen_ids.add(review_id)

    submitted = str(item.get("submissionTime", ""))
    date = submitted[:10] if len(submitted) >= 10 else ""

    records.append({
        "review_id": review_id,
        "title": title,
        "body": body,
        "date": date,
        "rating": rating,
        "source_platform": "Best Buy Canada",
        "reviewer_name": item.get("reviewerName", ""),
    })

output_path.parent.mkdir(parents=True, exist_ok=True)
df = pd.DataFrame(records, columns=[
    "review_id", "title", "body", "date", "rating",
    "source_platform", "reviewer_name"
])
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"Unique reviews extracted: {len(df)}")
print(f"CSV saved to: {output_path.resolve()}")
print(f"Duplicate review IDs: {df['review_id'].duplicated().sum()}")

if len(df) < 50:
    print("WARNING: This saved HTML does not contain 50 unique reviews.")
    print("Capture additional review pages before submitting Task 1.")
else:
    print("The 50-review minimum is met.")

