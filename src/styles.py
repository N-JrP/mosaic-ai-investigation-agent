import streamlit as st


def load_styles() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top right, rgba(14, 165, 233, 0.12), transparent 30%),
                radial-gradient(circle at bottom left, rgba(245, 158, 11, 0.10), transparent 28%),
                #F7F4EE;
        }

        [data-testid="stHeader"] {
            background: rgba(247, 244, 238, 0);
        }

        .block-container {
            padding-top: 0.7rem;
            padding-bottom: 0.4rem;
            padding-left: 1.4rem;
            padding-right: 1.4rem;
        }

        h1, h2, h3, h4, p, label, span {
            color: #172033;
        }

        h1 {
            margin-bottom: 0.1rem;
        }

        h3 {
            margin-top: 0.2rem;
            margin-bottom: 0.25rem;
        }

        h4 {
            margin-top: 0.15rem;
            margin-bottom: 0.15rem;
        }

        .subtitle {
            color: #475569;
            font-size: 0.9rem;
            margin-bottom: 0.35rem;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, 170px);
            gap: 10px;
            margin-top: 0.2rem;
        }

        .metric-card {
            background: linear-gradient(135deg, #FFFFFF 0%, #EAF7FF 100%);
            border: 1px solid rgba(14, 165, 233, 0.28);
            border-radius: 16px;
            padding: 10px 13px;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
            min-height: 58px;
        }

        .metric-label {
            color: #64748B;
            font-size: 0.74rem;
            margin-bottom: 0.12rem;
        }

        .metric-value {
            color: #0F172A;
            font-size: 1.22rem;
            font-weight: 750;
            line-height: 1.05;
        }

        .glass-card {
            background: linear-gradient(135deg, #FFFFFF 0%, #FFF7E6 100%);
            border: 1px solid rgba(245, 158, 11, 0.30);
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
            min-height: 120px;
        }

        .answer-card {
            background: linear-gradient(135deg, #FFFFFF 0%, #EAF7FF 100%);
            border: 1px solid rgba(14, 165, 233, 0.32);
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: 0 8px 22px rgba(14, 165, 233, 0.10);
            min-height: 105px;
        }

        .card-label {
            font-size: 0.75rem;
            color: #0284C7;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.3rem;
        }

        .card-text {
            color: #172033;
            font-size: 0.92rem;
            line-height: 1.35;
        }

        .workflow-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 13px;
            font-weight: 600;
            color: #0369A1;
            margin-top: 6px;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 14px;
            overflow: hidden;
        }

        .stButton button {
            border-radius: 12px;
            height: 38px;
            font-weight: 650;
            background: #0EA5E9;
            color: white;
            border: 0;
        }

        div[data-testid="stExpander"] {
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )