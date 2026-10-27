"""
Query loader — loads and manages analytical SQL queries from the sql/ directory.
"""

import pathlib
import re
from config import SQL_DIR


class QueryBundle:
    """Represents a named query with metadata."""

    def __init__(self, name: str, category: str, sql: str, description: str = "", technique: str = ""):
        self.name = name
        self.category = category
        self.sql = sql.strip()
        self.description = description
        self.technique = technique


def parse_sql_file(filepath: pathlib.Path) -> list:
    """
    Parse a SQL file into individual QueryBundle objects.
    Comments at the top describe metadata. Queries are separated by blank lines.
    """
    if not filepath.exists():
        return []

    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Extract header metadata
    description = ""
    technique = ""
    header_end = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("--"):
            cleaned = stripped.lstrip("- ").strip()
            if cleaned.lower().startswith("business question"):
                parts = cleaned.split(":", 1)
                description = parts[1].strip() if len(parts) > 1 else cleaned
            elif cleaned.lower().startswith("technique"):
                parts = cleaned.split(":", 1)
                technique = parts[1].strip() if len(parts) > 1 else cleaned
            header_end = i
        else:
            break

    # Split content into query blocks separated by blank lines after semicolons
    sql_text = "\n".join(lines[header_end:]).strip()
    raw_blocks = re.split(r';\n\s*\n', sql_text)

    queries = []
    for block in raw_blocks:
        # Clean the block
        block = block.strip()
        if not block:
            continue

        # Remove trailing comments and whitespace
        block_lines = block.split("\n")
        clean_lines = [l for l in block_lines if not l.strip().startswith("--")]
        clean_sql = "\n".join(clean_lines).strip()

        if not clean_sql:
            continue

        # Ensure semicolon at end
        if not clean_sql.rstrip().endswith(";"):
            clean_sql += ";"

        # Get first comment line as the query name
        name = "Query"
        for line in block_lines:
            stripped = line.strip()
            if stripped.startswith("--") and len(stripped) > 3:
                potential = stripped.lstrip("- ").strip()
                if potential and not potential.lower().startswith("business") and not potential.lower().startswith("technique"):
                    name = potential[:80]
                    break

        cat_key = filepath.stem
        # Remove leading number prefix (e.g., "01_data_quality" -> "data_quality")
        import re as re_stem
        stem_clean = re_stem.sub(r'^\d+_', '', cat_key)
        cat_name = stem_clean.replace("_", " ").title()

        queries.append(QueryBundle(
            name=name,
            category=cat_name,
            sql=clean_sql,
            description=description,
            technique=technique,
        ))

    return queries


def load_all_queries() -> dict:
    """
    Load all SQL queries from the sql/ directory.
    Returns a dict organized by category.
    """
    sql_dir = pathlib.Path(SQL_DIR)
    if not sql_dir.exists():
        return {}

    queries_by_category = {}

    for filepath in sorted(sql_dir.glob("*.sql")):
        queries = parse_sql_file(filepath)
        if queries:
            cat_name = queries[0].category
            queries_by_category[cat_name] = queries

    return queries_by_category


def get_query_by_index(category: str, index: int) -> QueryBundle:
    """Get a specific query by category name and index."""
    all_queries = load_all_queries()
    if category in all_queries and index < len(all_queries[category]):
        return all_queries[category][index]
    return None