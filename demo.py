"""
Zero-setup demo: creates a small sample SQLite database, scans it with
SQLiteScanner, and writes the discovered metadata to metadata_output.json.

Run with:
    python demo.py
"""
import os
import sqlite3

from scanner.sqlite_demo import SQLiteScanner
from scanner.exporter import export_json, print_summary

DB_PATH = "demo.db"
OUTPUT_PATH = "metadata_output.json"


def build_sample_database(path: str):
    if os.path.exists(path):
        os.remove(path)

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute(
        """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            created_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
        """
    )

    conn.commit()
    conn.close()


def main():
    print("Creating sample SQLite database...\n")
    build_sample_database(DB_PATH)

    print("Scanning database for metadata...\n")
    scanner = SQLiteScanner(path=DB_PATH)
    metadata = scanner.scan()

    print_summary(metadata)
    export_json(metadata, OUTPUT_PATH)
    print(f"Metadata written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
