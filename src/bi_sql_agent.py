import duckdb
import pandas as pd

from sql_guard import add_limit, validate_sql


DB_FILE = "warehouse/analytics.duckdb"


def generate_sql_from_question(question: str) -> str:
    question_lower = question.lower()

    if "review" in question_lower and "revenue" in question_lower:
        return """
            SELECT
                product_category_name_english,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(AVG(review_score), 2) AS avg_review_score,
                COUNT(DISTINCT order_id) AS total_orders
            FROM v_olist_business
            WHERE product_category_name_english IS NOT NULL
            GROUP BY product_category_name_english
            HAVING COUNT(DISTINCT order_id) >= 20
            ORDER BY total_revenue DESC, avg_review_score ASC
        """

    if "delay" in question_lower or "late" in question_lower or "delivery" in question_lower:
        return """
            SELECT
                customer_state,
                ROUND(AVG(delivery_delay_days), 2) AS avg_delivery_delay_days,
                COUNT(DISTINCT order_id) AS total_orders
            FROM v_olist_business
            WHERE delivery_delay_days IS NOT NULL
            GROUP BY customer_state
            ORDER BY avg_delivery_delay_days DESC
        """

    if "payment" in question_lower:
        return """
            SELECT
                payment_type,
                COUNT(*) AS total_payments,
                ROUND(SUM(payment_value), 2) AS total_payment_value
            FROM olist_payments
            GROUP BY payment_type
            ORDER BY total_payments DESC
        """

    if "month" in question_lower or "trend" in question_lower:
        return """
            SELECT
                DATE_TRUNC('month', order_purchase_timestamp) AS revenue_month,
                ROUND(SUM(revenue), 2) AS total_revenue,
                COUNT(DISTINCT order_id) AS total_orders
            FROM v_olist_business
            GROUP BY revenue_month
            ORDER BY revenue_month
        """

    if "seller" in question_lower:
        return """
            SELECT
                seller_id,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(AVG(review_score), 2) AS avg_review_score,
                COUNT(DISTINCT order_id) AS total_orders
            FROM v_olist_business
            GROUP BY seller_id
            HAVING COUNT(DISTINCT order_id) >= 10
            ORDER BY total_revenue DESC
        """

    return """
        SELECT
            product_category_name_english,
            ROUND(SUM(revenue), 2) AS total_revenue,
            COUNT(DISTINCT order_id) AS total_orders
        FROM v_olist_business
        WHERE product_category_name_english IS NOT NULL
        GROUP BY product_category_name_english
        ORDER BY total_revenue DESC
    """


def run_sql(sql: str) -> pd.DataFrame:
    sql = add_limit(sql)

    is_valid, message = validate_sql(sql)
    if not is_valid:
        raise ValueError(message)

    conn = duckdb.connect(DB_FILE)
    result_df = conn.execute(sql).fetchdf()
    conn.close()

    return result_df


def explain_result(question: str, result_df: pd.DataFrame) -> str:
    if result_df.empty:
        return "No matching result was found for this question."

    row_count = len(result_df)
    top_row = result_df.iloc[0].to_dict()

    return (
        f"Mosaic found {row_count} matching business segments in the real Olist dataset. "
        f"The strongest signal is {top_row}. "
        "Use this as a starting point to review performance, customer experience, and the next business action."
    )


def answer_business_question(question: str) -> tuple[pd.DataFrame, str, str]:
    sql = generate_sql_from_question(question)
    result_df = run_sql(sql)
    explanation = explain_result(question, result_df)

    return result_df, sql, explanation


if __name__ == "__main__":
    sample_question = "Which product categories have high revenue but low review scores?"

    result, sql_used, explanation_text = answer_business_question(sample_question)

    print("QUESTION:")
    print(sample_question)

    print("\nSQL:")
    print(sql_used)

    print("\nRESULT:")
    print(result.head())

    print("\nEXPLANATION:")
    print(explanation_text)

