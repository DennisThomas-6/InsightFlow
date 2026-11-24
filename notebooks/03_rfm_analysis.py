from pathlib import Path
import pandas as pd

# Find and load the prepared customer purchase data.
project_root = Path(__file__).resolve().parents[1]
file_path = (
    project_root
    / "data"
    / "processed"
    / "retail_customer_purchases.csv"
)

customer_sales_df = pd.read_csv(
    file_path,
    parse_dates=["InvoiceDate"],
    dtype={
        "CustomerID": "string",
        "InvoiceNo": "string",
    },
)

# Use the day after the latest transaction as the reference point.
latest_purchase = customer_sales_df["InvoiceDate"].max()
reference_date = latest_purchase.normalize() + pd.Timedelta(days=1)

# Calculate one row of RFM measures for each customer.
rfm = customer_sales_df.groupby("CustomerID").agg(
    LastPurchase=("InvoiceDate", "max"),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("LineAmount", "sum"),
)

rfm["Recency"] = (
    reference_date - rfm["LastPurchase"].dt.normalize()
).dt.days

# Arrange the columns for readability.
rfm = rfm[["LastPurchase", "Recency", "Frequency", "Monetary"]]

print("\nRFM REFERENCE DATE")
print(reference_date.date())

print("\nFIRST 10 CUSTOMER RFM RECORDS")
print(rfm.head(10).to_string())

print("\nRFM SUMMARY")
print(rfm[["Recency", "Frequency", "Monetary"]].describe().to_string())

print(f"\nCustomers analysed: {len(rfm):,}")

# Count how many customers have each purchase frequency.
print("\nCUSTOMER FREQUENCY COUNTS")
print(
    rfm["Frequency"]
    .value_counts()
    .sort_index()
    .head(10)
    .to_string()
)

# Score recency: fewer days means a higher score.
rfm["R_Score"] = pd.cut(
    rfm["Recency"],
    bins=[0, 18, 51, 142, float("inf")],
    labels=[4, 3, 2, 1],
).astype(int)

# Score frequency: more distinct invoices means a higher score.
rfm["F_Score"] = pd.cut(
    rfm["Frequency"],
    bins=[0, 1, 2, 5, float("inf")],
    labels=[1, 2, 3, 4],
).astype(int)

# Score monetary value using the observed quartile boundaries.
rfm["M_Score"] = pd.cut(
    rfm["Monetary"],
    bins=[float("-inf"), 307.415, 674.485, 1661.74, float("inf")],
    labels=[1, 2, 3, 4],
).astype(int)

# Combine the three scores into a label, such as "423".
rfm["RFM_Score"] = (
    rfm["R_Score"].astype(str)
    + rfm["F_Score"].astype(str)
    + rfm["M_Score"].astype(str)
)

print("\nFIRST 10 CUSTOMERS WITH RFM SCORES")
print(
    rfm[
        ["Recency", "Frequency", "Monetary",
         "R_Score", "F_Score", "M_Score", "RFM_Score"]
    ]
    .head(10)
    .to_string()
)

print("\nSCORE DISTRIBUTIONS")
for column in ["R_Score", "F_Score", "M_Score"]:
    print(f"\n{column}")
    print(rfm[column].value_counts().sort_index().to_string())


    # Assign each customer to one segment using recency and frequency.
def assign_segment(row):
    r = row["R_Score"]
    f = row["F_Score"]

    if r == 4 and f == 4:
        return "Champions"

    if r >= 3 and f >= 3:
        return "Loyal customers"

    if r >= 3 and f <= 2:
        return "Recent / occasional"

    if r <= 2 and f >= 3:
        return "At risk"

    return "Inactive / occasional"


rfm["Segment"] = rfm.apply(assign_segment, axis=1)

# Summarise customers and purchase value by segment.
segment_summary = (
    rfm.groupby("Segment")
    .agg(
        Customers=("Frequency", "size"),
        AverageRecency=("Recency", "mean"),
        AverageFrequency=("Frequency", "mean"),
        TotalPurchaseValue=("Monetary", "sum"),
        MedianPurchaseValue=("Monetary", "median"),
    )
    .sort_values("Customers", ascending=False)
)

print("\nCUSTOMER SEGMENT SUMMARY")
print(segment_summary.round(2).to_string())

print(f"\nTotal segmented customers: {segment_summary['Customers'].sum():,}")

# Save customer-level results and the segment summary.
output_dir = project_root / "data" / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

rfm.to_csv(output_dir / "customer_rfm_segments.csv")
segment_summary.to_csv(output_dir / "segment_summary.csv")

print("\nRFM results saved successfully.")