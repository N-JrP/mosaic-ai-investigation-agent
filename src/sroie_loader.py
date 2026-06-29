import json
from pathlib import Path

import duckdb
import pandas as pd


SROIE_ROOT = Path("data/raw/sroie/_extract/SROIE2019")
DB_FILE = "warehouse/analytics.duckdb"


def load_entity_file(entity_file: Path) -> dict:
    try:
        return json.loads(entity_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def build_sroie_dataframe() -> pd.DataFrame:
    rows = []

    for split in ["train", "test"]:
        entities_dir = SROIE_ROOT / split / "entities"
        images_dir = SROIE_ROOT / split / "img"

        for entity_file in sorted(entities_dir.glob("*.txt")):
            receipt_id = entity_file.stem
            entity_data = load_entity_file(entity_file)

            image_path = None
            for extension in [".jpg", ".png", ".jpeg"]:
                candidate = images_dir / f"{receipt_id}{extension}"
                if candidate.exists():
                    image_path = candidate.as_posix()
                    break

            company = entity_data.get("company", "")
            date = entity_data.get("date", "")
            address = entity_data.get("address", "")
            total = entity_data.get("total", "")

            missing_fields = []
            for field_name, value in {
                "company": company,
                "date": date,
                "address": address,
                "total": total,
            }.items():
                if not str(value).strip():
                    missing_fields.append(field_name)

            rows.append(
                {
                    "receipt_id": receipt_id,
                    "split": split,
                    "image_path": image_path,
                    "company": company,
                    "date": date,
                    "address": address,
                    "total": total,
                    "missing_fields": ", ".join(missing_fields),
                    "needs_review": len(missing_fields) > 0,
                    "search_text": f"{company} {date} {address} {total}".strip(),
                }
            )

    return pd.DataFrame(rows)


def load_sroie_tables() -> None:
    df = build_sroie_dataframe()

    if df.empty:
        raise ValueError("No SROIE entity files found. Check data/raw/sroie/_extract/SROIE2019.")

    conn = duckdb.connect(DB_FILE)

    conn.execute("CREATE OR REPLACE TABLE sroie_receipts AS SELECT * FROM df")

    conn.execute(
        """
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
        """
    )

    conn.close()

    print(f"Loaded {len(df)} SROIE receipts into DuckDB.")


if __name__ == "__main__":
    load_sroie_tables()