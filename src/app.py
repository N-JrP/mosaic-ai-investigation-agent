import pickle
from pathlib import Path
from demo_data import ensure_demo_data
import duckdb
import faiss
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sentence_transformers import SentenceTransformer

from bi_sql_agent import answer_business_question
from styles import load_styles


DB_FILE = "warehouse/analytics.duckdb"
INDEX_FILE = "warehouse/faiss_index.bin"
DOCS_FILE = "warehouse/retrieval_docs.pkl"


st.set_page_config(page_title="Mosaic - Document & BI Agent", layout="wide")
load_styles()

st.title("Mosaic")
st.markdown(
    '<div class="subtitle">AI Investigation Agent that combines structured business data and document evidence into explainable enterprise recommendations.</div>',
    unsafe_allow_html=True,
)


def table_exists(table_name: str) -> bool:
    if not Path(DB_FILE).exists():
        return False

    conn = duckdb.connect(DB_FILE)
    result = conn.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = ?
        """,
        [table_name],
    ).fetchone()[0]
    conn.close()

    return result > 0


if (
    not table_exists("v_olist_business")
    or not table_exists("v_sroie_document_review")
    or not table_exists("olist_payments")
):
    ensure_demo_data()
else:
    conn = duckdb.connect(DB_FILE)
    demo_check = conn.execute("SELECT COUNT(DISTINCT order_id) FROM v_olist_business").fetchone()[0]
    conn.close()

    if demo_check < 20:
        ensure_demo_data()


def run_query(sql: str) -> pd.DataFrame:
    conn = duckdb.connect(DB_FILE)
    df = conn.execute(sql).fetchdf()
    conn.close()
    return df


def metric_grid(metric_row_data) -> None:
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Orders</div>
                <div class="metric-value">{int(metric_row_data['total_orders']):,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Customers</div>
                <div class="metric-value">{int(metric_row_data['total_customers']):,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Sellers</div>
                <div class="metric-value">{int(metric_row_data['total_sellers']):,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Revenue</div>
                <div class="metric-value">${metric_row_data['total_revenue']:,.0f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def answer_card(text: str) -> None:
    html = f'''
<div class="answer-card"><div class="card-label">Agent Findings</div><div class="card-text">{text}</div><hr style="margin:14px 0;border:none;border-top:1px solid rgba(2,132,199,.15);"><div class="card-label">Agent Workflow</div><div class="workflow-row"><span>Understand</span><span>→</span><span>Plan</span><span>→</span><span>Retrieve</span><span>→</span><span>Execute</span><span>→</span><span>Rank Evidence</span><span>→</span><span>Recommend</span></div></div>
'''
    st.markdown(html, unsafe_allow_html=True)

def next_action_card(question: str, result_df: pd.DataFrame) -> None:
    question_lower = question.lower()

    if "payment" in question_lower:
        action = "Credit card dominates payment behavior. Review checkout costs, card processing fees, and alternative payment adoption."
    elif "delay" in question_lower or "delivery" in question_lower:
        action = "Prioritize states with the longest delivery delays and review logistics partners, seller handling time, and customer expectations."
    elif "review" in question_lower:
        action = "Focus on high-revenue categories with weaker reviews because they may create the largest customer experience risk."
    elif "seller" in question_lower:
        action = "Review top sellers by revenue and satisfaction together before making account management or quality decisions."
    elif "month" in question_lower or "trend" in question_lower:
        action = "Use the revenue trend to identify growth periods, seasonality, and months that need deeper business review."
    else:
        action = "Start with the highest revenue categories, then compare customer reviews, delivery delays, and seller performance."

    st.markdown(
        f"""
        <div class="glass-card">
            <div class="card-label">Agent Recommendation</div>
            <div class="card-text">{action}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def evidence_card(question: str, result_df: pd.DataFrame) -> None:
    question_lower = question.lower()

    if "payment" in question_lower:
        source = "olist_payments table"
        view = "Payment behavior evidence"
    elif "seller" in question_lower:
        source = "v_olist_business view"
        view = "Seller revenue + review evidence"
    elif "delay" in question_lower or "delivery" in question_lower:
        source = "v_olist_business view"
        view = "Delivery timestamp evidence"
    elif "month" in question_lower or "trend" in question_lower:
        source = "v_olist_business view"
        view = "Monthly revenue trend evidence"
    else:
        source = "v_olist_business view"
        view = "Revenue and order evidence"

    st.markdown(
        f"""
<div class="glass-card">
    <div class="card-label">Evidence Trail</div>
    <div class="card-text">
        ✓ DuckDB warehouse<br>
        ✓ {source}<br>
        ✓ {view}<br>
        ✓ {len(result_df)} ranked records shown<br>
        ✓ SQL proof available below
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def show_compact_chart(df: pd.DataFrame) -> None:
    if df.empty:
        return

    chart_df = df.head(5).copy()
    numeric_columns = chart_df.select_dtypes(include=["number"]).columns.tolist()
    text_columns = chart_df.select_dtypes(exclude=["number"]).columns.tolist()

    if not numeric_columns or not text_columns:
        return

    label_col = text_columns[0]
    value_col = numeric_columns[0]

    fig = px.bar(
        chart_df.sort_values(value_col, ascending=True),
        x=value_col,
        y=label_col,
        orientation="h",
        text=value_col,
        title=f"Ranked evidence by {value_col}",
    )

    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")

    fig.update_layout(
        height=245,
        margin=dict(l=5, r=35, t=38, b=5),
        showlegend=False,
        xaxis_title="",
        yaxis_title="",
    )

    st.plotly_chart(fig, use_container_width=True)

tab_bi, tab_docs, tab_about = st.tabs(
    ["Business Investigation", "Document Investigation", "Architecture"]
)


with tab_bi:
    if not table_exists("v_olist_business"):
        st.warning("The Olist business view is not loaded yet. Run src/olist_loader.py first.")
    else:
        metrics_df = run_query(
            """
            SELECT
                COUNT(DISTINCT order_id) AS total_orders,
                COUNT(DISTINCT customer_id) AS total_customers,
                COUNT(DISTINCT seller_id) AS total_sellers,
                ROUND(SUM(revenue), 2) AS total_revenue
            FROM v_olist_business
            """
        )

        metric_row_data = metrics_df.iloc[0]

        example_questions = [
            "Which product categories bring the most revenue?",
            "Which product categories have high revenue but low review scores?",
            "Which states have the longest delivery delays?",
            "What are the most common payment methods?",
            "What is the monthly revenue trend?",
            "Which sellers should the business review first?",
        ]

        top_left, top_right = st.columns([0.48, 0.52])

        with top_left:
            st.markdown("### Business Investigation")
            ask_col, run_col = st.columns([5, 1])

            with ask_col:
                selected_question = st.selectbox(
                    "Business question",
                    example_questions,
                    label_visibility="collapsed",
                )

            with run_col:
                run_clicked = st.button("Investigate", use_container_width=True)

        with top_right:
            metric_grid(metric_row_data)

        if run_clicked:
            result_df, sql_used, explanation = answer_business_question(selected_question)
            display_df = result_df.head(5)
        else:
            display_df = run_query(
                """
                SELECT
                    product_category_name_english,
                    ROUND(SUM(revenue), 2) AS total_revenue,
                    COUNT(DISTINCT order_id) AS total_orders
                FROM v_olist_business
                WHERE product_category_name_english IS NOT NULL
                GROUP BY product_category_name_english
                ORDER BY total_revenue DESC
                LIMIT 5
                """
            )
            sql_used = """
SELECT
    product_category_name_english,
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders
FROM v_olist_business
WHERE product_category_name_english IS NOT NULL
GROUP BY product_category_name_english
ORDER BY total_revenue DESC
LIMIT 5
            """
            explanation = (
                "Mosaic found the strongest revenue categories in the real Olist dataset. "
                "These categories give the business a clear starting point for reviewing growth, customer experience, and seller performance."
            )

        left_col, right_col = st.columns([0.48, 0.52])

        with left_col:
            st.markdown("### Insight")
            answer_card(explanation)

            st.markdown("#### Evidence Ranking")
            st.dataframe(display_df, use_container_width=True, height=145)

            with st.expander("Evidence Query (Verified SQL)", expanded=False):
                st.code(sql_used, language="sql")

        with right_col:
            st.markdown("### Visual")
            with st.container(border=True):
                show_compact_chart(display_df)

            next_action_card(selected_question, display_df)
            evidence_card(selected_question, display_df)


with tab_docs:
    st.header("Document Investigation")

    if table_exists("v_sroie_document_review"):
        docs_metrics_df = run_query(
            """
            SELECT
                COUNT(*) AS total_receipts,
                SUM(CASE WHEN needs_review THEN 1 ELSE 0 END) AS needs_review_count,
                COUNT(DISTINCT company) AS unique_companies
            FROM v_sroie_document_review
            """
        )

        docs_metric_row = docs_metrics_df.iloc[0]

        top_left, top_right = st.columns([0.34, 0.66])

        with top_left:
            st.markdown(
                f"""
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-label">Receipts</div>
                        <div class="metric-value">{int(docs_metric_row['total_receipts']):,}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Need Review</div>
                        <div class="metric-value">{int(docs_metric_row['needs_review_count']):,}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Companies</div>
                        <div class="metric-value">{int(docs_metric_row['unique_companies']):,}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with top_right:
            search_col, filter_col = st.columns([2, 1])

            with search_col:
                receipt_search = st.text_input(
                    "Document tab supports receipt search and review filtering",
                    placeholder="Search company, date, address, or total",
                    label_visibility="collapsed",
                )

            with filter_col:
                review_filter = st.selectbox(
                    "Review status",
                    ["All receipts", "Needs review only", "Clean only"],
                    label_visibility="collapsed",
                )

        where_clauses = []
        params = []

        if receipt_search.strip():
            where_clauses.append("LOWER(search_text) LIKE ?")
            params.append(f"%{receipt_search.lower().strip()}%")

        if review_filter == "Needs review only":
            where_clauses.append("needs_review = true")
        elif review_filter == "Clean only":
            where_clauses.append("needs_review = false")

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        conn = duckdb.connect(DB_FILE)
        receipts_df = conn.execute(
            f"""
            SELECT
                receipt_id,
                company,
                date,
                total,
                needs_review,
                missing_fields
            FROM v_sroie_document_review
            {where_sql}
            ORDER BY needs_review DESC, receipt_id
            LIMIT 15
            """,
            params,
        ).fetchdf()
        conn.close()

        left_col, right_col = st.columns([0.62, 0.38])

        with left_col:
            st.markdown("### Documents Requiring Review")
            st.dataframe(receipts_df, use_container_width=True, height=290)

        with right_col:
            visible_review_count = int(receipts_df["needs_review"].sum()) if not receipts_df.empty else 0
            visible_count = len(receipts_df)

            st.markdown(
                f"""
                <div class="answer-card">
                    <div class="card-label">Document Review Summary</div>
                    <div class="card-text">
                        Mosaic flags receipts with missing fields so teams can review only the documents that need attention.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            missing_summary_df = run_query(
                """
                SELECT
                    missing_fields,
                    COUNT(*) AS receipts
                FROM v_sroie_document_review
                WHERE needs_review = true
                GROUP BY missing_fields
                ORDER BY receipts DESC
                """
            )

            st.markdown("#### Missing Field Summary")
            st.dataframe(missing_summary_df, use_container_width=True, height=150)

    else:
        st.info(
            "SROIE receipt data is not loaded yet. Run `src/sroie_loader.py` to connect the document intelligence tab."
        )

with tab_about:
    st.header("Architecture")

    st.markdown(
        """
<div class="answer-card">
    <div class="card-label">Enterprise Investigation Agent</div>
    <div class="card-text">
        Mosaic combines structured business data and document-derived evidence into explainable recommendations.
        Every conclusion is traceable through ranked evidence, verified SQL, and reviewable document signals.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Compact Agent Pipeline")

    st.markdown(
        """
<div class="glass-card">
    <div class="card-text" style="font-size:0.95rem; line-height:1.7;">
        <b>User Question</b> → <b>Business Investigation Agent</b> → <b>Source Selection</b>
        → <b>SQL Generation + Validation</b> → <b>DuckDB Execution</b>
        → <b>Evidence Ranking</b> → <b>Agent Recommendation</b> → <b>Human Decision</b>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### System Components")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
<div class="answer-card">
    <div class="card-label">Business Layer</div>
    <div class="card-text">
        ✓ Olist dataset<br>
        ✓ DuckDB warehouse<br>
        ✓ <code>v_olist_business</code><br>
        ✓ SQL-backed analysis
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
<div class="answer-card">
    <div class="card-label">Document Layer</div>
    <div class="card-text">
        ✓ SROIE receipts<br>
        ✓ Extracted fields<br>
        ✓ Missing-field flags<br>
        ✓ Human review queue
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
<div class="answer-card">
    <div class="card-label">Agent Layer</div>
    <div class="card-text">
        ✓ Plan<br>
        ✓ Retrieve<br>
        ✓ Execute<br>
        ✓ Rank evidence<br>
        ✓ Recommend
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("### Why this matters")

    st.markdown(
        """
<div class="glass-card">
    <div class="card-text">
        Mosaic demonstrates an explainable AI investigation workflow where business metrics and document-derived evidence are combined into transparent recommendations. Every conclusion is traceable back to verified SQL and source documents, enabling analysts to investigate rather than simply view dashboards.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )



