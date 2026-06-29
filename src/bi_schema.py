import duckdb


DB_FILE = "warehouse/analytics.duckdb"


def get_schema_context() -> str:
    conn = duckdb.connect(DB_FILE)

    tables = conn.execute("SHOW TABLES").fetchdf()["name"].tolist()

    schema_lines = []

    for table in tables:
        columns_df = conn.execute(f"DESCRIBE {table}").fetchdf()

        column_text = ", ".join(
            [
                f"{row['column_name']} ({row['column_type']})"
                for _, row in columns_df.iterrows()
            ]
        )

        schema_lines.append(f"{table}: {column_text}")

    conn.close()

    return "\n".join(schema_lines)


if __name__ == "__main__":
    print(get_schema_context())