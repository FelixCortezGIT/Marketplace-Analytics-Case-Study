import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os

matplotlib.rcParams['font.family'] = 'DejaVu Sans'

# === SETUP ===
os.makedirs("cleaned_data", exist_ok=True)

# === LOAD DATA ===
orders = pd.read_csv("data/orders.csv")
products = pd.read_csv("data/products.csv")
countries = pd.read_csv("data/countries.csv")

products = products.rename(columns={"cost": "product_cost"})

# === MERGE ===
df = orders.merge(products, on="product_id").merge(countries, on="country_id")
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.to_period("M")
df["profit"] = df["revenue"] - df["product_cost"]

print(f"Loaded {len(df)} orders")

# === 1. DUPLICATES ===
dupes = orders[orders.duplicated(subset=["date", "product_id", "country_id", "revenue"], keep=False)]
print(f"✓ Found {len(dupes)} duplicate orders")
dupes.to_csv("cleaned_data/01_duplicates.csv", index=False)
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(["Unique Orders", "Duplicate Orders"], [len(orders) - len(dupes), len(dupes)], color=["#2aa8cc", "#cc0000"])
ax.set_title("Duplicate Orders Detection", fontsize=16, fontweight="bold")
ax.set_ylabel("Count")
for i, val in enumerate([len(orders) - len(dupes), len(dupes)]):
    ax.text(i, val + 2, str(val), ha="center", fontsize=12)
plt.tight_layout()
plt.savefig("cleaned_data/01_duplicates.png", dpi=150)
plt.close()
df = df.drop_duplicates(subset=["date", "product_id", "country_id", "revenue"])
print("✓ 01_duplicates.png")

# === 2. REVENUE BY COUNTRY ===
rev_country = df.groupby("country_name")["revenue"].sum().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(rev_country.index, rev_country.values, color="#2aa8cc")
ax.set_title("Revenue by Country", fontsize=16, fontweight="bold")
ax.set_xlabel("Total Revenue (EUR)")
for bar, val in zip(bars, rev_country.values):
    ax.text(val + 500, bar.get_y() + bar.get_height()/2, f"€{val:,.0f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig("cleaned_data/02_revenue_by_country.png", dpi=150)
plt.close()
print("✓ 02_revenue_by_country.png")

# === 3. TOP PRODUCTS ===
top_products = df.groupby("name")["revenue"].sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(range(len(top_products)), top_products.values, color="#0d3b47")
ax.set_xticks(range(len(top_products)))
ax.set_xticklabels(top_products.index, rotation=30, ha="right", fontsize=9)
ax.set_title("Top 10 Products by Revenue", fontsize=16, fontweight="bold")
ax.set_ylabel("Total Revenue (EUR)")
for bar, val in zip(bars, top_products.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200, f"€{val:,.0f}", ha="center", fontsize=8)
plt.tight_layout()
plt.savefig("cleaned_data/03_top_products.png", dpi=150)
plt.close()
print("✓ 03_top_products.png")

# === 4. LOW MARGIN PRODUCTS ===
low_margin = df.groupby("name")["margin_pct"].mean().sort_values().head(10)
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(range(len(low_margin)), low_margin.values, color="#cc0000")
ax.set_xticks(range(len(low_margin)))
ax.set_xticklabels(low_margin.index, rotation=30, ha="right", fontsize=9)
ax.set_title("Low Margin Products (Bottom 10)", fontsize=16, fontweight="bold")
ax.set_ylabel("Average Margin (%)")
ax.axhline(y=low_margin.mean(), color="black", linestyle="--", label="Average")
for bar, val in zip(bars, low_margin.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, f"{val:.1f}%", ha="center", fontsize=8)
plt.tight_layout()
plt.savefig("cleaned_data/04_low_margin_products.png", dpi=150)
plt.close()
print("✓ 04_low_margin_products.png")

# === 5. RETURN RATE BY COUNTRY ===
return_country = df.groupby("country_name")["returned"].mean() * 100
return_country = return_country.sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(return_country.index, return_country.values, color="#e67e22")
ax.set_title("Return Rate by Country (%)", fontsize=16, fontweight="bold")
ax.set_xlabel("Return Rate (%)")
ax.axvline(x=return_country.mean(), color="red", linestyle="--", label=f"Avg: {return_country.mean():.1f}%")
ax.legend()
for bar, val in zip(bars, return_country.values):
    ax.text(val + 0.1, bar.get_y() + bar.get_height()/2, f"{val:.1f}%", va="center", fontsize=9)
plt.tight_layout()
plt.savefig("cleaned_data/05_return_rate_by_country.png", dpi=150)
plt.close()
print("✓ 05_return_rate_by_country.png")

# === 6. RETURN RATE BY PRODUCT ===
return_product = df.groupby("name")["returned"].mean() * 100
return_product = return_product.sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(range(len(return_product)), return_product.values, color="#e74c3c")
ax.set_xticks(range(len(return_product)))
ax.set_xticklabels(return_product.index, rotation=30, ha="right", fontsize=9)
ax.set_title("Top 10 Products by Return Rate", fontsize=16, fontweight="bold")
ax.set_ylabel("Return Rate (%)")
for bar, val in zip(bars, return_product.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, f"{val:.1f}%", ha="center", fontsize=8)
plt.tight_layout()
plt.savefig("cleaned_data/06_return_rate_by_product.png", dpi=150)
plt.close()
print("✓ 06_return_rate_by_product.png")

# === 7. MONTHLY TREND ===
monthly = df.groupby("month")["revenue"].sum()
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(monthly.index.astype(str), monthly.values, marker="o", color="#2aa8cc", linewidth=2, markersize=6)
ax.fill_between(monthly.index.astype(str), monthly.values, alpha=0.2, color="#2aa8cc")
ax.set_title("Monthly Revenue Trend 2024", fontsize=16, fontweight="bold")
ax.set_ylabel("Revenue (EUR)")
ax.set_xlabel("Month")
plt.xticks(rotation=45)
for i, val in enumerate(monthly.values):
    ax.text(i, val + 500, f"€{val:,.0f}", ha="center", fontsize=7)
plt.tight_layout()
plt.savefig("cleaned_data/07_monthly_trend.png", dpi=150)
plt.close()
print("✓ 07_monthly_trend.png")

# === 8. REVENUE BY MARKETPLACE ===
rev_market = df.groupby("marketplace")["revenue"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 6))
colors = ["#FF9900", "#0057e7", "#00A650"]
wedges, texts, autotexts = ax.pie(rev_market.values, labels=rev_market.index, autopct="%1.1f%%", colors=colors, startangle=90)
ax.set_title("Revenue by Marketplace", fontsize=16, fontweight="bold")
plt.tight_layout()
plt.savefig("cleaned_data/08_revenue_by_marketplace.png", dpi=150)
plt.close()
print("✓ 08_revenue_by_marketplace.png")

# === 9. REVENUE BY CATEGORY ===
rev_cat = df.groupby("category")["revenue"].sum().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(rev_cat.index, rev_cat.values, color="#1b4332")
ax.set_title("Revenue by Category", fontsize=16, fontweight="bold")
ax.set_xlabel("Total Revenue (EUR)")
for bar, val in zip(bars, rev_cat.values):
    ax.text(val + 200, bar.get_y() + bar.get_height()/2, f"€{val:,.0f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig("cleaned_data/09_revenue_by_category.png", dpi=150)
plt.close()
print("✓ 09_revenue_by_category.png")

# === 10. MARGIN BY CATEGORY ===
margin_cat = df.groupby("category")["margin_pct"].mean().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(margin_cat.index, margin_cat.values, color="#145d72")
ax.set_title("Average Margin by Category (%)", fontsize=16, fontweight="bold")
ax.set_xlabel("Average Margin (%)")
for bar, val in zip(bars, margin_cat.values):
    ax.text(val + 0.2, bar.get_y() + bar.get_height()/2, f"{val:.1f}%", va="center", fontsize=9)
plt.tight_layout()
plt.savefig("cleaned_data/10_margin_by_category.png", dpi=150)
plt.close()
print("✓ 10_margin_by_category.png")

# === 11. PROFIT BY COUNTRY ===
profit_country = df.groupby("country_name")["profit"].sum().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(profit_country.index, profit_country.values, color="#0d3b47")
ax.set_title("Profit by Country", fontsize=16, fontweight="bold")
ax.set_xlabel("Total Profit (EUR)")
for bar, val in zip(bars, profit_country.values):
    ax.text(val + 100, bar.get_y() + bar.get_height()/2, f"€{val:,.0f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig("cleaned_data/11_profit_by_country.png", dpi=150)
plt.close()
print("✓ 11_profit_by_country.png")

# === 12. AVG ORDER VALUE BY COUNTRY ===
aov_country = df.groupby("country_name")["revenue"].mean().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(aov_country.index, aov_country.values, color="#2c7873")
ax.set_title("Average Order Value by Country", fontsize=16, fontweight="bold")
ax.set_xlabel("Average Order Value (EUR)")
for bar, val in zip(bars, aov_country.values):
    ax.text(val + 2, bar.get_y() + bar.get_height()/2, f"€{val:.2f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig("cleaned_data/12_avg_order_value_by_country.png", dpi=150)
plt.close()
print("✓ 12_avg_order_value_by_country.png")

# === 13. ORDERS BY COUNTRY ===
orders_country = df.groupby("country_name")["order_id"].count().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(orders_country.index, orders_country.values, color="#2aa8cc")
ax.set_title("Number of Orders by Country", fontsize=16, fontweight="bold")
ax.set_xlabel("Number of Orders")
for bar, val in zip(bars, orders_country.values):
    ax.text(val + 1, bar.get_y() + bar.get_height() / 2, str(val), va="center", fontsize=9)
plt.tight_layout()
plt.savefig("cleaned_data/13_orders_by_country.png", dpi=150)
plt.close()
print("✓ 13_orders_by_country.png")

# === 14. MONTHLY ORDERS TREND ===
monthly_orders = df.groupby("month")["order_id"].count()
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(monthly_orders.index.astype(str), monthly_orders.values, marker="o", color="#e67e22", linewidth=2, markersize=6)
ax.fill_between(monthly_orders.index.astype(str), monthly_orders.values, alpha=0.2, color="#e67e22")
ax.set_title("Monthly Orders Trend 2024", fontsize=16, fontweight="bold")
ax.set_ylabel("Number of Orders")
ax.set_xlabel("Month")
plt.xticks(rotation=45)
for i, val in enumerate(monthly_orders.values):
    ax.text(i, val + 1, str(val), ha="center", fontsize=8)
plt.tight_layout()
plt.savefig("cleaned_data/14_monthly_orders_trend.png", dpi=150)
plt.close()
print("✓ 14_monthly_orders_trend.png")

# === 15. UNITS SOLD BY PRODUCT ===
units_product = df.groupby("name")["quantity"].sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(range(len(units_product)), units_product.values, color="#1b4332")
ax.set_xticks(range(len(units_product)))
ax.set_xticklabels(units_product.index, rotation=30, ha="right", fontsize=9)
ax.set_title("Top 10 Products by Units Sold", fontsize=16, fontweight="bold")
ax.set_ylabel("Total Units Sold")
for bar, val in zip(bars, units_product.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, str(val), ha="center", fontsize=9)
plt.tight_layout()
plt.savefig("cleaned_data/15_units_sold_by_product.png", dpi=150)
plt.close()
print("✓ 15_units_sold_by_product.png")

# === 16. ORDERS BY MARKETPLACE ===
orders_market = df.groupby("marketplace")["order_id"].count().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 6))
colors = ["#FF9900", "#0057e7", "#00A650"]
bars = ax.bar(orders_market.index, orders_market.values, color=colors)
ax.set_title("Number of Orders by Marketplace", fontsize=16, fontweight="bold")
ax.set_ylabel("Number of Orders")
for bar, val in zip(bars, orders_market.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, str(val), ha="center", fontsize=12,
            fontweight="bold")
plt.tight_layout()
plt.savefig("cleaned_data/16_orders_by_marketplace.png", dpi=150)
plt.close()
print("✓ 16_orders_by_marketplace.png")

# === 17. HEATMAP - ORDERS BY MARKETPLACE x COUNTRY ===
heatmap_data = df.groupby(["country_name", "marketplace"])["order_id"].count().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(10, 7))
im = ax.imshow(heatmap_data.values, cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(len(heatmap_data.columns)))
ax.set_xticklabels(heatmap_data.columns, fontsize=11)
ax.set_yticks(range(len(heatmap_data.index)))
ax.set_yticklabels(heatmap_data.index, fontsize=10)
ax.set_title("Orders by Marketplace × Country", fontsize=16, fontweight="bold")
plt.colorbar(im, ax=ax, label="Number of Orders")
for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        ax.text(j, i, str(heatmap_data.values[i, j]), ha="center", va="center", fontsize=10, fontweight="bold")
plt.tight_layout()
plt.savefig("cleaned_data/17_heatmap_marketplace_country.png", dpi=150)
plt.close()
print("✓ 17_heatmap_marketplace_country.png")

# === 18. TOP CATEGORY BY COUNTRY ===
cat_country = df.groupby(["country_name", "category"])["revenue"].sum().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12, 7))
cat_country.plot(kind="bar", ax=ax, colormap="tab10")
ax.set_title("Revenue by Category per Country", fontsize=16, fontweight="bold")
ax.set_ylabel("Revenue (EUR)")
ax.set_xlabel("")
plt.xticks(rotation=30, ha="right")
ax.legend(title="Category", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig("cleaned_data/18_category_by_country.png", dpi=150)
plt.close()
print("✓ 18_category_by_country.png")

# === 19. UNITS SOLD BY CATEGORY ===
units_cat = df.groupby("category")["quantity"].sum().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(units_cat.index, units_cat.values, color="#145d72")
ax.set_title("Total Units Sold by Category", fontsize=16, fontweight="bold")
ax.set_xlabel("Total Units Sold")
for bar, val in zip(bars, units_cat.values):
    ax.text(val + 1, bar.get_y() + bar.get_height() / 2, str(val), va="center", fontsize=9)
plt.tight_layout()
plt.savefig("cleaned_data/19_units_sold_by_category.png", dpi=150)
plt.close()
print("✓ 19_units_sold_by_category.png")

# === SUMMARY ===
summary = df.groupby("country_name").agg(
    total_revenue=("revenue", "sum"),
    total_profit=("profit", "sum"),
    total_orders=("order_id", "count"),
    avg_margin=("margin_pct", "mean"),
    return_rate=("returned", "mean"),
    avg_order_value=("revenue", "mean")
).round(2)
summary["return_rate"] = (summary["return_rate"] * 100).round(2)
summary.to_csv("cleaned_data/summary.csv")
print("✓ summary.csv")

# Summary Graf
fig, ax1 = plt.subplots(figsize=(14, 7))
x = range(len(summary.index))
width = 0.3

bars1 = ax1.bar([i - width for i in x], summary["total_revenue"], width, label="Revenue (EUR)", color="#2aa8cc")
bars2 = ax1.bar(x, summary["total_profit"], width, label="Profit (EUR)", color="#0d3b47")
ax1.set_ylabel("EUR")
ax1.set_xticks(x)
ax1.set_xticklabels(summary.index, rotation=30, ha="right")
ax1.set_title("Country Performance Overview", fontsize=16, fontweight="bold")

ax2 = ax1.twinx()
ax2.bar([i + width for i in x], summary["return_rate"], width, label="Return Rate (%)", color="#cc0000", alpha=0.7)
ax2.set_ylabel("Return Rate (%)")

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.tight_layout()
plt.savefig("cleaned_data/20_summary_overview.png", dpi=150)
plt.close()
print("✓ 20_summary_overview.png")

print("\n✅ All done! Check the cleaned_data/ folder.")
