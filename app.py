#!/usr/bin/env python3
"""
Text2SQL: Natural Language to SQL Query Generator

A CLI app that loads CSV data, converts natural language questions to SQL,
executes the queries, and returns results.
"""

import argparse
import sqlite3
import sys
from pathlib import Path

import pandas as pd

from model_client import DistilLabsLLM


def load_csv_to_sqlite(csv_paths: list[str], conn: sqlite3.Connection) -> dict[str, str]:
    """
    Load CSV files into SQLite database and return schema information.

    Returns a dict mapping table names to their CREATE TABLE statements.
    """
    schemas = {}

    for csv_path in csv_paths:
        path = Path(csv_path)
        table_name = path.stem.replace("-", "_").replace(" ", "_").lower()

        df = pd.read_csv(csv_path)
        df.to_sql(table_name, conn, index=False, if_exists="replace")

        # Generate CREATE TABLE statement from DataFrame
        columns = []
        for col in df.columns:
            dtype = df[col].dtype
            if pd.api.types.is_integer_dtype(dtype):
                sql_type = "INTEGER"
            elif pd.api.types.is_float_dtype(dtype):
                sql_type = "REAL"
            else:
                sql_type = "TEXT"
            columns.append(f"  {col} {sql_type}")

        create_stmt = f"CREATE TABLE {table_name} (\n" + ",\n".join(columns) + "\n);"
        schemas[table_name] = create_stmt

    return schemas


def format_question(schema: str, question: str) -> str:
    """Format the schema and question into the expected input format."""
    return f"""Schema:
{schema}

Question: {question}"""


def execute_query(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    """Execute SQL query and return results as DataFrame."""
    return pd.read_sql_query(sql, conn)


def main():
    parser = argparse.ArgumentParser(
        description="Text2SQL: Query CSV data using natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query a single CSV file
  python app.py --csv data/employees.csv --question "How many employees are there?"

  # Query multiple CSV files (for JOINs)
  python app.py --csv data/orders.csv --csv data/customers.csv \\
                --question "Show total orders per customer"

  # Use a different model
  python app.py --csv data.csv --model distil-qwen3-4b-text2sql-gguf \\
                --question "What is the average salary?"
        """,
    )
    parser.add_argument(
        "--csv",
        type=str,
        action="append",
        required=True,
        help="Path to CSV file (can be specified multiple times for multiple tables)",
    )
    parser.add_argument(
        "--question",
        type=str,
        required=True,
        help="Natural language question about the data",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="distil-qwen3-4b-text2sql-gguf-4bit",
        help="Model name (default: distil-qwen3-4b-text2sql-gguf-4bit)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=11434,
        help="Ollama server port (default: 11434)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default="EMPTY",
        help="API key (default: EMPTY for local Ollama)",
    )
    parser.add_argument(
        "--show-sql",
        action="store_true",
        help="Print the generated SQL query",
    )

    args = parser.parse_args()

    # Validate CSV files exist
    for csv_path in args.csv:
        if not Path(csv_path).exists():
            print(f"Error: CSV file not found: {csv_path}", file=sys.stderr)
            sys.exit(1)

    # Create in-memory SQLite database and load CSV data
    conn = sqlite3.connect(":memory:")

    try:
        schemas = load_csv_to_sqlite(args.csv, conn)
    except Exception as e:
        print(f"Error loading CSV files: {e}", file=sys.stderr)
        sys.exit(1)

    # Combine all schemas
    full_schema = "\n\n".join(schemas.values())

    # Initialize model client
    client = DistilLabsLLM(
        model_name=args.model,
        api_key=args.api_key,
        port=args.port,
    )

    # Generate SQL from natural language
    formatted_input = format_question(full_schema, args.question)

    try:
        sql = client.invoke(formatted_input).strip()
    except Exception as e:
        print(f"Error generating SQL: {e}", file=sys.stderr)
        sys.exit(1)

    if args.show_sql:
        print(f"Generated SQL: {sql}\n")

    # Execute the query
    try:
        results = execute_query(conn, sql)
        print(results.to_string(index=False))
    except Exception as e:
        print(f"Error executing query: {e}", file=sys.stderr)
        print(f"Generated SQL was: {sql}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
