
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#Read our sample reviews
df = pd.read_csv("data/reviews.csv")

#Create a sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

#Analyze each review
def get_sentiment(review):
    scores = analyzer.polarity_scores(str(review))
    compound = scores["compound"]
    print("Review:", review, "| Compound score:", compound)
    if compound >= 0.05:
        return "positive"
    elif compound <= -0.05:
        return "negative"
    else:
        return "neutral"

df["sentiment"] = df["review_body"].apply(get_sentiment)

df["needs_review"] = (
    ((df["rating"] >= 4) & (df["sentiment"] == "negative")) |
    ((df["rating"] <= 2) & (df["sentiment"] == "positive")) |
    ((df["rating"] >= 4) & (df["sentiment"] == "neutral")) |
    ((df["rating"] <= 2) & (df["sentiment"] == "neutral"))
)

#Save the analyzed reviews
df.to_csv("data/reviews_with_sentiment.csv", index=False)

#print(df[["review_body", "rating", "sentiment"]])
print(df[["review_body", "rating", "sentiment", "needs_review"]])
print("\nSaved to data/reviews_with_sentiment.csv")

print("\nReviews that need manual checking:")
print(
    df[df["needs_review"]][
        ["review_body", "rating", "sentiment"]
    ]
)