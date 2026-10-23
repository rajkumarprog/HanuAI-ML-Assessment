
from pathlib import Path
import pandas as pd

#Create folders for the project outputs
Path("data").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

#Sample data to test our workflow
#These are examples,NOT real BestBuy reviews
reviews = [
    {
        "review_title":"Great battery",
        "review_body":"The battery lasts all day.",
        "review_date":"2026-10-20",
        "rating":5,
        "source_platform":"Best Buy Canada",
        "reviewer_name":"Sample User"
    },
    {
        "review_title":"Poor screen",
        "review_body":"The screen stopped working.",
        "review_date":"2026-10-21",
        "rating":1,
        "source_platform":"Best Buy Canada",
        "reviewer_name":"Example User"
    }
]

#Convert the list of dictionaries into a table
df = pd.DataFrame(reviews)

#Save the table as a CSV file
df.to_csv("data/reviews.csv", index=False)

print(df)
print("\nSample dataset saved to data/reviews.csv")
