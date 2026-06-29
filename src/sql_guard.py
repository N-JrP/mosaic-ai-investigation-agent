import re
import sqlparse


BLOCKED_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "copy",
    "attach",
    "detach",
    "pragma",
    "truncate",
    "merge",
    "replace",
}

ALLOWED_STARTS = ("select", "with")


def validate_sql(sql: str) -> tuple[bool, str]:
    if not sql or not sql.strip():
        return False, "SQL is empty."

    cleaned_sql = sql.strip().strip(";")
    lowered_sql = cleaned_sql.lower()

    statements = sqlparse.split(cleaned_sql)
    if len(statements) != 1:
        return False, "Only one SQL statement is allowed."

    if not lowered_sql.startswith(ALLOWED_STARTS):
        return False, "Only SELECT or WITH queries are allowed."

    tokens = set(re.findall(r"[a-zA-Z_]+", lowered_sql))
    blocked = tokens.intersection(BLOCKED_KEYWORDS)

    if blocked:
        blocked_words = ", ".join(sorted(blocked))
        return False, f"Blocked keyword found: {blocked_words}"

    return True, "SQL passed safety check."


def add_limit(sql: str, limit: int = 100) -> str:
    cleaned_sql = sql.strip().rstrip(";")
    lowered_sql = cleaned_sql.lower()

    if " limit " in lowered_sql:
        return cleaned_sql

    return f"{cleaned_sql} LIMIT {limit}"