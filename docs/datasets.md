# Datasets

Mosaic uses two real public datasets.

| Dataset | Folder | Purpose |
|---|---|---|
| SROIE Receipt Dataset | `data/raw/sroie/` | Document understanding, field extraction, receipt search |
| Olist Brazilian E-Commerce Dataset | `data/raw/olist/` | Business questions, SQL analysis, charts, recommendations |

## SROIE Receipt Dataset

Used for the document side of Mosaic.

It will be used to test:

- vendor extraction
- date extraction
- total amount extraction
- receipt search
- missing-field detection

## Olist Brazilian E-Commerce Dataset

Used for the business data side of Mosaic.

The Olist CSV files are stored locally in:

`data/raw/olist/`

The dataset has been loaded into DuckDB using:

`src/olist_loader.py`

The main business view is:

`v_olist_business`

This view connects orders, customers, products, sellers, payments, reviews, and delivery dates so Mosaic can answer real business questions.

## Olist files used

| File |
|---|
| `olist_orders_dataset.csv` |
| `olist_order_items_dataset.csv` |
| `olist_customers_dataset.csv` |
| `olist_products_dataset.csv` |
| `olist_order_payments_dataset.csv` |
| `olist_order_reviews_dataset.csv` |
| `olist_sellers_dataset.csv` |
| `product_category_name_translation.csv` |