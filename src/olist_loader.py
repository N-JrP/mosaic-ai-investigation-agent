from pathlib import Path

import duckdb


RAW_OLIST_DIR = Path("data/raw/olist")
DB_FILE = "warehouse/analytics.duckdb"


OLIST_FILES = {
    "olist_orders": "olist_orders_dataset.csv",
    "olist_order_items": "olist_order_items_dataset.csv",
    "olist_customers": "olist_customers_dataset.csv",
    "olist_products": "olist_products_dataset.csv",
    "olist_payments": "olist_order_payments_dataset.csv",
    "olist_reviews": "olist_order_reviews_dataset.csv",
    "olist_sellers": "olist_sellers_dataset.csv",
    "olist_category_translation": "product_category_name_translation.csv",
}


def validate_olist_files() -> list[str]:
    missing_files = []

    for file_name in OLIST_FILES.values():
        file_path = RAW_OLIST_DIR / file_name
        if not file_path.exists():
            missing_files.append(str(file_path))

    return missing_files


def load_olist_tables() -> None:
    missing_files = validate_olist_files()

    if missing_files:
        missing_text = "\n".join(missing_files)
        raise FileNotFoundError(
            "Missing Olist dataset files. Please place the required CSV files here:\n"
            "data/raw/olist/\n\n"
            f"Missing files:\n{missing_text}"
        )

    conn = duckdb.connect(DB_FILE)

    for table_name, file_name in OLIST_FILES.items():
        file_path = RAW_OLIST_DIR / file_name
        conn.execute(
            f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT *
            FROM read_csv_auto('{file_path.as_posix()}', ignore_errors=true)
            """
        )

    create_olist_business_view(conn)

    conn.close()
    print("Olist tables loaded into DuckDB successfully.")


def create_olist_business_view(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(
        """
        CREATE OR REPLACE VIEW v_olist_business AS
        SELECT
            orders.order_id,
            orders.order_status,
            CAST(orders.order_purchase_timestamp AS TIMESTAMP) AS order_purchase_timestamp,
            CAST(orders.order_delivered_customer_date AS TIMESTAMP) AS order_delivered_customer_date,
            CAST(orders.order_estimated_delivery_date AS TIMESTAMP) AS order_estimated_delivery_date,

            customers.customer_id,
            customers.customer_city,
            customers.customer_state,

            items.product_id,
            items.seller_id,
            items.price,
            items.freight_value,
            (items.price + items.freight_value) AS revenue,

            products.product_category_name,
            COALESCE(
                translation.product_category_name_english,
                products.product_category_name
            ) AS product_category_name_english,

            reviews.review_score,

            DATE_DIFF(
                'day',
                CAST(orders.order_estimated_delivery_date AS TIMESTAMP),
                CAST(orders.order_delivered_customer_date AS TIMESTAMP)
            ) AS delivery_delay_days

        FROM olist_orders AS orders
        LEFT JOIN olist_customers AS customers
            ON orders.customer_id = customers.customer_id
        LEFT JOIN olist_order_items AS items
            ON orders.order_id = items.order_id
        LEFT JOIN olist_products AS products
            ON items.product_id = products.product_id
        LEFT JOIN olist_category_translation AS translation
            ON products.product_category_name = translation.product_category_name
        LEFT JOIN olist_reviews AS reviews
            ON orders.order_id = reviews.order_id
        WHERE orders.order_status = 'delivered'
        """
    )


if __name__ == "__main__":
    load_olist_tables()