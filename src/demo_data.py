from pathlib import Path
import duckdb
import pandas as pd

DB_FILE = "warehouse/analytics.duckdb"

def ensure_demo_data() -> None:
    Path("warehouse").mkdir(exist_ok=True)

    conn = duckdb.connect(DB_FILE)

    conn.execute("""
        CREATE OR REPLACE TABLE demo_business AS
        SELECT * FROM (
            VALUES
            ('health_beauty', 1417268.99, 4.19, '8647'),
            ('watches_gifts', 1265552.91, 4.07, '5495'),
            ('bed_bath_table', 1241489.78, 3.92, '9272'),
            ('sports_leisure', 1124637.43, 4.17, '7530'),
            ('computers_accessories', 1041314.27, 3.98, '6530')
        ) AS t(product_category_name_english, revenue, review_score, order_id)
    """)

    conn.execute("""
        CREATE OR REPLACE VIEW v_olist_business AS
        SELECT
            product_category_name_english,
            revenue,
            review_score,
            order_id,
            'demo_customer' AS customer_id,
            'demo_seller' AS seller_id,
            'credit_card' AS payment_type,
            'SP' AS customer_state,
            DATE '2018-01-01' AS order_purchase_timestamp,
            DATE '2018-01-05' AS order_delivered_customer_date,
            DATE '2018-01-07' AS order_estimated_delivery_date
        FROM demo_business
    """)

    receipts = pd.DataFrame([
        {
            "receipt_id": "X00016469620",
            "split": "demo",
            "company": "MR D.I.Y. (JOHOR) SDN BHD",
            "date": "12-01-19",
            "total": "33.90",
            "needs_review": False,
            "missing_fields": "",
            "image_path": "",
            "search_text": "MR D.I.Y. JOHOR 12-01-19 33.90",
        },
        {
            "receipt_id": "X00016469623",
            "split": "demo",
            "company": "MR D.I.Y. (M) SDN BHD",
            "date": "18-11-18",
            "total": "30.90",
            "needs_review": False,
            "missing_fields": "",
            "image_path": "",
            "search_text": "MR D.I.Y. 18-11-18 30.90",
        },
        {
            "receipt_id": "X51005230617",
            "split": "demo",
            "company": "GERBANG ALAF RESTAURANTS SDN BHD",
            "date": "18/01/2018",
            "total": "26.60",
            "needs_review": True,
            "missing_fields": "address",
            "image_path": "",
            "search_text": "GERBANG ALAF RESTAURANTS 18/01/2018 26.60",
        },
    ])

    conn.execute("CREATE OR REPLACE TABLE sroie_receipts AS SELECT * FROM receipts")

    conn.execute("""
        CREATE OR REPLACE VIEW v_sroie_document_review AS
        SELECT
            receipt_id,
            split,
            company,
            date,
            total,
            missing_fields,
            needs_review,
            image_path,
            search_text
        FROM sroie_receipts
    """)

    conn.close()
