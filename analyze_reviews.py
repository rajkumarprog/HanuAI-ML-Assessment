"""Clean collected review records, assign lexicon sentiment and aspect tags, and export analysis."""
import re
from pathlib import Path
import pandas as pd

DATA = Path("data")
RAW = DATA / "bestbuy_reviews_raw.csv"
OUT = DATA / "bestbuy_reviews_with_sentiment.csv"

POS = set("great excellent amazing love perfect comfortable clear easy reliable recommend worth fantastic good happy impressive fantastic awesome".split())
NEG = set("bad poor terrible hate uncomfortable broken issue problem disappointing defect fail failed noisy painful expensive return stopped worst fragile".split())

ASPECTS = {
    "Design & Build Quality": ["design", "build", "quality", "material", "durable", "hinge", "plastic"],
    "Comfort & Fit": ["comfort", "comfortable", "fit", "ear", "headband", "pressure"],
    "Sound Quality": ["sound", "audio", "bass", "treble", "music", "noise cancelling", "anc"],
    "Battery & Charging": ["battery", "charge", "charging", "usb", "hours"],
    "Connectivity & Controls": ["bluetooth", "connect", "connection", "pair", "app", "button", "control"],
    "Price & Value": ["price", "expensive", "value", "money", "cost", "worth"],
    "Reliability & Defects": ["broken", "defect", "stopped", "fail", "issue", "problem", "return", "warranty", "hinge"],
    "Recommendation & Satisfaction": ["recommend", "love", "happy", "satisfied", "worth", "disappoint"]
}

def clean(value):
    value = "" if pd.isna(value) else str(value)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()

def sentiment(text):
    tokens = re.findall(r"[a-z']+", text.lower())
    pos = sum(t in POS for t in tokens)
    neg = sum(t in NEG for t in tokens)
    score = pos - neg
    label = "Positive" if score >= 2 else "Negative" if score <= -2 else "Neutral"
    return label, score

def tag_aspects(text, label):
    low = text.lower()
    suffix = {"Positive":"Pos", "Negative":"Neg", "Neutral":"Neu"}[label]
    tags = [f"{aspect} ({suffix})" for aspect, terms in ASPECTS.items() if any(term in low for term in terms)]
    return "; ".join(tags) if tags else f"General Review ({suffix})"

def main():
    if not RAW.exists():
        raise FileNotFoundError(f"{RAW} not found. Run collect_bestbuy_reviews.py first.")
    df = pd.read_csv(RAW)
    if len(df) < 50:
        print(f"WARNING: only {len(df)} rows. Assignment requires at least 50 genuine reviews.")
    if "review_body" not in df.columns:
        raise ValueError("Expected review_body column in raw CSV.")
    for col in ["review_title", "review_body", "reviewer_name", "review_date"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].map(clean)
    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["star_rating"] = pd.to_numeric(df.get("star_rating"), errors="coerce")
    df["combined_text"] = (df["review_title"].fillna("") + " " + df["review_body"].fillna("")).str.strip()
    scores = df["combined_text"].map(sentiment)
    df["sentiment"] = scores.map(lambda x: x[0])
    df["sentiment_score"] = scores.map(lambda x: x[1])
    df["aspect_sentiment_tags"] = df.apply(lambda r: tag_aspects(r["combined_text"], r["sentiment"]), axis=1)
    df = df.drop_duplicates(subset=["review_id"]).reset_index(drop=True)
    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    print("Rows exported:", len(df))
    print("Output:", OUT.resolve())
    print("\nSentiment counts:\n", df["sentiment"].value_counts(dropna=False))
    print("\nRating distribution:\n", df["star_rating"].value_counts(dropna=False).sort_index())
    print("\nAspect-tag frequency:")
    counts = df["aspect_sentiment_tags"].str.split("; ").explode().value_counts()
    print(counts.head(20).to_string())
    print("\nMissing required fields:")
    required = ["review_id","review_title","review_body","review_date","star_rating","source_platform","reviewer_name"]
    print(df.reindex(columns=required).isna().sum().to_string())

if __name__ == "__main__":
    main()
