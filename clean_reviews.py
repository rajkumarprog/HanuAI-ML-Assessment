
import pandas as pd

# Load the original review dataset
df = pd.read_csv("data/reviews.csv")

print("Original number of reviews:", len(df))

# Remove duplicate rows
df = df.drop_duplicates()

# Remove reviews with missing review text
df = df.dropna(subset=["review_body"])

# Remove reviews with empty text
df["review_body"] = df["review_body"].astype(str).str.strip()
df = df[df["review_body"] != ""]

# Keep only valid star ratings from 1 to 5
df = df[df["rating"].between(1, 5)]

print("Reviews after cleaning:", len(df))

# Save the cleaned dataset
df.to_csv("data/cleaned_reviews.csv", index=False)

print("Cleaned dataset saved to data/cleaned_reviews.csv")
