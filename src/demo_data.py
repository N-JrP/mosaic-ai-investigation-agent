from pathlib import Path
from datetime import date
import duckdb
import pandas as pd

DB_FILE = "warehouse/analytics.duckdb"


def ensure_demo_data() -> None:
    Path("warehouse").mkdir(exist_ok=True)

    rows = []
    categories = [
        ("health_beauty", 1417268.99, 4.19, "seller_health", "SP"),
        ("watches_gifts", 1265552.91, 4.07, "seller_watch", "RJ"),
        ("bed_bath_table", 1241489.78, 3.92, "seller_bed", "MG"),
        ("sports_leisure", 1124637.43, 4.17, "seller_sports", "BA"),
        ("computers_accessories", 1041314.27, 3.98, "seller_computers", "PR"),
    ]

    order_num = 1

    for category, total_revenue, review_score, seller_id, state in categories:
        for i in range(30):
            rows.append(
                {
                    "order_id": f"ORD{order_num:05d}",
                    "customer_id": f"CUST{order_num:05d}",
                    "seller_id": seller_id,
                    "product_category_name_english": category,
                    "revenue": round(total_revenue / 30, 2),
                    "review_score": review_score,
                    "customer_state": state,
                    "delivery_delay_days": [8, 7, 6, 5, 4][i % 5],
                    "order_purchase_timestamp": date(2018, (i % 12) + 1, 1),
                    "order_delivered_customer_date": date(2018, (i % 12) + 1, 10),
                    "order_estimated_delivery_date": date(2018, (i % 12) + 1, 5),
                }
            )
            order_num += 1

    business_df = pd.DataFrame(rows)

    payments_df = pd.DataFrame(
        [
            {"payment_type": "credit_card", "payment_value": 12542084.19}
            for _ in range(80)
        ]
        + [
            {"payment_type": "boleto", "payment_value": 2869361.27}
            for _ in range(20)
        ]
        + [
            {"payment_type": "voucher", "payment_value": 379436.87}
            for _ in range(6)
        ]
        + [
            {"payment_type": "debit_card", "payment_value": 217989.79}
            for _ in range(2)
        ]
        + [
            {"payment_type": "not_defined", "payment_value": 0.0}
        ]
    )

    receipts_df = pd.DataFrame(
        [
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
                "receipt_id": "X00016469672",
                "split": "demo",
                "company": "SOON HUAT MACHINERY ENTERPRISE",
                "date": "11/01/2019",
                "total": "327.00",
                "needs_review": False,
                "missing_fields": "",
                "image_path": "",
                "search_text": "SOON HUAT MACHINERY ENTERPRISE 11/01/2019 327.00",
            },
            {
                "receipt_id": "X00016469619",
                "split": "demo",
                "company": "INDAH GIFT & HOME DECO",
                "date": "19/10/2018",
                "total": "60.30",
                "needs_review": False,
                "missing_fields": "",
                "image_path": "",
                "search_text": "INDAH GIFT HOME DECO 19/10/2018 60.30",
            },
            {
                "receipt_id": "X00016469612",
                "split": "demo",
                "company": "BOOK TA .K (TAMAN DAYA) SDN BHD",
                "date": "25/12/2018",
                "total": "9.00",
                "needs_review": False,
                "missing_fields": "",
                "image_path": "",
                "search_text": "BOOK TA K TAMAN DAYA 25/12/2018 9.00",
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
            {
                "receipt_id": "X51005433522",
                "split": "demo",
                "company": "UNIHAKKA INTERNATIONAL SDN BHD",
                "date": "10 MAR 2018",
                "total": "",
                "needs_review": True,
                "missing_fields": "total",
                "image_path": "",
                "search_text": "UNIHAKKA INTERNATIONAL SDN BHD 10 MAR 2018",
            },
            {
                "receipt_id": "X51005663280",
                "split": "demo",
                "company": "T.A.S LEISURE SDN BHD",
                "date": "30 DEC 17",
                "total": "102.40",
                "needs_review": True,
                "missing_fields": "address",
                "image_path": "",
                "search_text": "T.A.S LEISURE SDN BHD 30 DEC 17 102.40",
            },
            {
                "receipt_id": "X00016469669",
                "split": "demo",
                "company": "ABC HO TRADING",
                "date": "09/01/2019",
                "total": "31.00",
                "needs_review": False,
                "missing_fields": "",
                "image_path": "",
                "search_text": "ABC HO TRADING 09/01/2019 31.00",
            },
            {
                "receipt_id": "X00016469676",
                "split": "demo",
                "company": "S.H.H. MOTOR (SUNGAI RENGIT) SDN. BHD.",
                "date": "23-01-2019",
                "total": "20.00",
                "needs_review": False,
                "missing_fields": "",
                "image_path": "",
                "search_text": "S.H.H. MOTOR SUNGAI RENGIT 23-01-2019 20.00",
            },
        ]
    )
    conn = duckdb.connect(DB_FILE)

    conn.execute("CREATE OR REPLACE TABLE demo_olist_business AS SELECT * FROM business_df")
    conn.execute("CREATE OR REPLACE TABLE olist_payments AS SELECT * FROM payments_df")
    conn.execute("CREATE OR REPLACE TABLE sroie_receipts AS SELECT * FROM receipts_df")

    conn.execute("""
        CREATE OR REPLACE VIEW v_olist_business AS
        SELECT * FROM demo_olist_business
    """)

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

