from pathlib import Path
import pandas as pd

# Find the prepared purchase data.
project_root = Path(__file__).resolve().parents[1]
file_path = project_root / "data" / "processed" / "retail_purchases.csv"

# Load invoice numbers as text and invoice dates as dates.
sales_df = pd.read_csv(
    file_path,
    parse_dates=["InvoiceDate"],
    dtype={"InvoiceNo": "string"},
)

# Calculate monthly purchase value and distinct invoice count.
sales_df["Month"] = sales_df["InvoiceDate"].dt.to_period("M")

monthly_summary = sales_df.groupby("Month").agg(
    PurchaseTotal=("LineAmount", "sum"),
    InvoiceCount=("InvoiceNo", "nunique"),
)

print("\nMONTHLY PURCHASE SUMMARY")
print(monthly_summary.to_string())

# Calculate purchase value and quantity for each item.
product_summary = (
    sales_df.groupby(["StockCode", "Description"], dropna=False)
    .agg(
        PurchaseTotal=("LineAmount", "sum"),
        QuantityPurchased=("Quantity", "sum"),
    )
    .sort_values("PurchaseTotal", ascending=False)
)

print("\nTOP 10 ITEMS BY PURCHASE VALUE")
print(product_summary.head(10).to_string())

# Calculate purchase value and distinct invoices for each country.
country_summary = (
    sales_df.groupby("Country", dropna=False)
    .agg(
        PurchaseTotal=("LineAmount", "sum"),
        InvoiceCount=("InvoiceNo", "nunique"),
    )
    .sort_values("PurchaseTotal", ascending=False)
)

print("\nTOP 10 COUNTRIES BY PURCHASE VALUE")
print(country_summary.head(10).to_string())

# Inspect entries that may not be physical products.
special_items = sales_df[
    sales_df["StockCode"].isin(["DOT", "POST", "M"])
]

print("\nSPECIAL ITEM EXAMPLES")
print(
    special_items[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "LineAmount"]
    ]
    .head(10)
    .to_string(index=False)
)

# Inspect the purchase lines with the largest quantities.
largest_quantities = sales_df.nlargest(10, "Quantity")

print("\nTOP 10 LINES BY QUANTITY")
print(
    largest_quantities[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "LineAmount"]
    ]
    .to_string(index=False)
)

# Exclude the three inspected special codes from a working product view.
special_codes = ["DOT", "POST", "M"]

product_sales_df = sales_df.loc[
    ~sales_df["StockCode"].isin(special_codes)
].copy()

print("\nWORKING PRODUCT VIEW")
print(f"Original purchase rows: {len(sales_df):,}")
print(f"Rows after excluding special codes: {len(product_sales_df):,}")
print(
    "Excluded purchase value:",
    f"{sales_df['LineAmount'].sum() - product_sales_df['LineAmount'].sum():,.2f}",
)

# Rank the remaining items by purchase value.
cleaner_product_summary = (
    product_sales_df.groupby(["StockCode", "Description"], dropna=False)
    .agg(
        PurchaseTotal=("LineAmount", "sum"),
        QuantityPurchased=("Quantity", "sum"),
    )
    .sort_values("PurchaseTotal", ascending=False)
)

print("\nTOP 10 ITEMS AFTER SPECIAL-CODE EXCLUSION")
print(cleaner_product_summary.head(10).to_string())

# Identify the two large lines using invoice number and stock code.
large_line_mask = (
    (
        (product_sales_df["InvoiceNo"] == "581483")
        & (product_sales_df["StockCode"] == "23843")
        & (product_sales_df["Quantity"] == 80995)
        & (product_sales_df["UnitPrice"] == 2.08)
    )
    |
    (
        (product_sales_df["InvoiceNo"] == "541431")
        & (product_sales_df["StockCode"] == "23166")
        & (product_sales_df["Quantity"] == 74215)
        & (product_sales_df["UnitPrice"] == 1.04)
    )
)

large_lines = product_sales_df.loc[large_line_mask]

print("\nLARGE-LINE COMPARISON")
print(f"Matching lines: {len(large_lines):,}")
print(f"Matching purchase value: {large_lines['LineAmount'].sum():,.2f}")

# Create a separate comparison without those specific lines.
comparison_df = product_sales_df.loc[~large_line_mask].copy()

comparison_summary = (
    comparison_df.groupby(["StockCode", "Description"], dropna=False)
    .agg(
        PurchaseTotal=("LineAmount", "sum"),
        QuantityPurchased=("Quantity", "sum"),
    )
    .sort_values("PurchaseTotal", ascending=False)
)

print("\nTOP 10 ITEMS WITHOUT THE TWO LARGE LINES")
print(comparison_summary.head(10).to_string())