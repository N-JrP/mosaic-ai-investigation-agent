# Project Structure

| Folder / File | Purpose |
|---|---|
| `data/raw/sroie/` | Real receipt/document dataset files |
| `data/raw/olist/` | Real e-commerce dataset files |
| `data/raw/legacy/` | Old sample document file kept for reference |
| `warehouse/` | DuckDB database and generated retrieval files |
| `src/` | Python code for ingestion, transformation, search, analytics, and app logic |
| `dbt_project/` | dbt models for structured analytics |
| `docs/` | Project notes, datasets, and use cases |
| `evaluation/` | Test questions and evaluation results |
| `prompts/` | Prompts for natural-language SQL and explanation generation |
| `screenshots/` | Screenshots for README and portfolio proof |
| `README.md` | Main project explanation |
| `requirements.txt` | Python dependencies |

## Current upgrade direction

Mosaic keeps the existing document intelligence base and adds two real-data layers:

| Layer | Dataset | Goal |
|---|---|---|
| Document Intelligence | SROIE Receipt Dataset | Search and extract information from real receipt documents |
| Business Intelligence | Olist E-Commerce Dataset | Ask plain-English business questions and produce SQL-backed insights |