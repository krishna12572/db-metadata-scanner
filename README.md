# DB Metadata Scanner

A lightweight Python tool that connects to a relational database (PostgreSQL or MySQL)
and automatically collects metadata about its schema — tables, columns, data types,
primary keys, and foreign key relationships — then exports the result as structured JSON.

This is the kind of "scanner" used by data catalog platforms to crawl a data source
and build a searchable map of where data lives, without requiring anyone to manually
document the schema.

## Why I built this

Data catalog products need a reliable way to discover what tables and columns exist
inside a company's databases. This project is a small proof-of-concept of that idea:
point it at a database connection, and it returns a clean, structured snapshot of the
schema that could be ingested into a catalog or search index.

## Features

- Supports PostgreSQL and MySQL via a common interface (`BaseScanner`)
- Extracts: schema name, table name, column name, data type, nullability,
  primary key flags, and foreign key relationships
- Outputs both a JSON file and a human-readable summary in the terminal
- Modular design: adding a new data source means implementing one small class
- Includes a sample SQLite scanner so the project can run end-to-end with zero setup

## Project structure

```
db-metadata-scanner/
├── README.md
├── requirements.txt
├── scanner/
│   ├── __init__.py
│   ├── base.py          # abstract base class all scanners implement
│   ├── postgres.py      # PostgreSQL scanner
│   ├── mysql.py         # MySQL scanner
│   ├── sqlite_demo.py   # SQLite scanner used for the demo (no setup required)
│   └── exporter.py      # writes metadata to JSON / prints summary
├── demo.py               # creates a sample SQLite DB and scans it
└── main.py                # CLI entrypoint for real Postgres/MySQL connections
```

## Quick demo (no database needed)

```bash
pip install -r requirements.txt
python demo.py
```

This creates a small sample SQLite database (`demo.db`), scans it, and writes
`metadata_output.json` with the discovered schema.

## Using it against a real database

```bash
python main.py --engine postgres \
    --host localhost --port 5432 \
    --dbname mydb --user myuser --password mypass \
    --output metadata_output.json
```

```bash
python main.py --engine mysql \
    --host localhost --port 3306 \
    --dbname mydb --user myuser --password mypass \
    --output metadata_output.json
```

## Example output

```json
{
  "source": "sqlite",
  "scanned_at": "2026-06-30T12:00:00",
  "tables": [
    {
      "schema": "main",
      "name": "customers",
      "columns": [
        {"name": "id", "type": "INTEGER", "nullable": false, "primary_key": true},
        {"name": "name", "type": "TEXT", "nullable": true, "primary_key": false},
        {"name": "email", "type": "TEXT", "nullable": true, "primary_key": false}
      ],
      "foreign_keys": []
    }
  ]
}
```

## Possible next steps

- Add scanners for Snowflake / BigQuery via their respective Python SDKs
- Push results into a search index (e.g., Elasticsearch) instead of a flat JSON file
- Add incremental scanning so only schema changes are re-collected
- Wrap the scanner as a packaged CLI binary for easy distribution to client environments
