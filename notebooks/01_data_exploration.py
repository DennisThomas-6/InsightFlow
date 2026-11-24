from ucimlrepo import fetch_ucirepo
import pandas as pd

retail = fetch_ucirepo(id=352)
raw_df = retail.data.original.copy()

# Preserve raw data and work on a separate copy.
df = raw_df.copy()

# Convert dates; invalid values become NaT (missing datetime).
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)

# Convert numeric identifiers to nullable integers, then strings.
# Missing IDs remain missing rather than becoming the text "nan".
df["CustomerID"] = (
    df["CustomerID"].astype("Int64").astype("string")
)

# Mark cancellation invoices without deleting them.
df["IsCancellation"] = (
    df["InvoiceNo"]
    .astype("string")
    .str.upper()
    .str.startswith("C", na=False)
)

print("Rows:", len(df))
print("\nUpdated data types:")
print(df.dtypes)

print("\nDate range:")
print(df["InvoiceDate"].min(), "to", df["InvoiceDate"].max())

print("\nQuality checks:")
checks = {
    "Unparseable or missing dates": df["InvoiceDate"].isna().sum(),
    "Missing customer IDs": df["CustomerID"].isna().sum(),
    "Missing descriptions": df["Description"].isna().sum(),
    "Exact duplicate rows in raw data": raw_df.duplicated().sum(),
    "Cancellation lines": df["IsCancellation"].sum(),
    "Negative quantities": (df["Quantity"] < 0).sum(),
    "Zero quantities": (df["Quantity"] == 0).sum(),
    "Negative unit prices": (df["UnitPrice"] < 0).sum(),
    "Zero unit prices": (df["UnitPrice"] == 0).sum(),
}

for label, count in checks.items():
    print(f"{label}: {count:,}")

print("\nDuplicate examples:")
print(
    raw_df.loc[raw_df.duplicated(keep=False)]
    .head(10)
    .to_string(index=False)
)

print("\nSuspicious transaction examples:")
suspicious = (
    df["IsCancellation"]
    | (df["Quantity"] <= 0)
    | (df["UnitPrice"] <= 0)
)

print(
    df.loc[
        suspicious,
        ["InvoiceNo", "StockCode", "Quantity", "UnitPrice", "IsCancellation"],
    ]
    .head(10)
    .to_string(index=False)
)
from pathlib import Path

# Calculate the value of each transaction line.
df["LineAmount"] = df["Quantity"] * df["UnitPrice"]

# Select paid purchase lines.
purchase_mask = (
    df["InvoiceDate"].notna()
    & ~df["IsCancellation"]
    & (df["Quantity"] > 0)
    & (df["UnitPrice"] > 0)
)

sales_df = df.loc[purchase_mask].copy()

# Select purchases that have a customer ID.
customer_sales_df = sales_df.loc[
    sales_df["CustomerID"].notna()
].copy()

# Compare sales totals with and without exact duplicate rows.
original_columns = raw_df.columns.tolist()
sales_without_duplicates = sales_df.drop_duplicates(
    subset=original_columns
)

purchase_total = sales_df["LineAmount"].sum()
deduplicated_total = sales_without_duplicates["LineAmount"].sum()

print("\nANALYSIS DATASETS")
print(f"Prepared rows: {len(df):,}")
print(f"Paid purchase rows: {len(sales_df):,}")
print(f"Customer purchase rows: {len(customer_sales_df):,}")
print(f"Unique customers: {customer_sales_df['CustomerID'].nunique():,}")
print(f"Distinct purchase invoices: {sales_df['InvoiceNo'].nunique():,}")
print(f"Paid purchase line total: {purchase_total:,.2f}")

print("\nDUPLICATE SENSITIVITY")
print(
    "Rows removed if deduplicated:",
    f"{len(sales_df) - len(sales_without_duplicates):,}",
)
print(
    "Difference in purchase total:",
    f"{purchase_total - deduplicated_total:,.2f}",
)

# Create folders and save the datasets.
project_root = Path(__file__).resolve().parents[1]
raw_dir = project_root / "data" / "raw"
processed_dir = project_root / "data" / "processed"

raw_dir.mkdir(parents=True, exist_ok=True)
processed_dir.mkdir(parents=True, exist_ok=True)

raw_df.to_csv(raw_dir / "online_retail_raw.csv", index=False)
df.to_csv(processed_dir / "retail_prepared.csv", index=False)
sales_df.to_csv(processed_dir / "retail_purchases.csv", index=False)
customer_sales_df.to_csv(
    processed_dir / "retail_customer_purchases.csv",
    index=False,
)

print("\nDatasets saved successfully.")
