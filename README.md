markdown# DB Metadata Scanner

A lightweight Python tool that connects to a relational database (PostgreSQL or MySQL)
and automatically collects metadata about its schema — tables, columns, data types,
primary keys, and foreign key relationships — then exports the result as structured JSON.

This is the kind of "scanner" used by data catalog platforms to crawl a data source
and build a searchable map of where data lives, without requiring anyone to manually
document the schema.

> 🇯🇵 [日本語版 README はこちら](#日本語)

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
db-metadata-scanner/
├── README.md
├── requirements.txt
├── scanner/
│   ├── init.py
│   ├── base.py          # abstract base class all scanners implement
│   ├── postgres.py      # PostgreSQL scanner
│   ├── mysql.py         # MySQL scanner
│   ├── sqlite_demo.py   # SQLite scanner used for the demo (no setup required)
│   └── exporter.py      # writes metadata to JSON / prints summary
├── demo.py               # creates a sample SQLite DB and scans it
└── main.py                # CLI entrypoint for real Postgres/MySQL connections

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
  "scanned_at": "2026-06-30T07:57:00Z",
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
    },
    {
      "schema": "main",
      "name": "orders",
      "columns": [
        {"name": "id", "type": "INTEGER", "nullable": false, "primary_key": true},
        {"name": "customer_id", "type": "INTEGER", "nullable": false, "primary_key": false},
        {"name": "total_amount", "type": "REAL", "nullable": false, "primary_key": false},
        {"name": "created_at", "type": "TEXT", "nullable": true, "primary_key": false}
      ],
      "foreign_keys": [
        {"column": "customer_id", "references_table": "customers", "references_column": "id"}
      ]
    },
    {
      "schema": "main",
      "name": "order_items",
      "columns": [
        {"name": "id", "type": "INTEGER", "nullable": false, "primary_key": true},
        {"name": "order_id", "type": "INTEGER", "nullable": false, "primary_key": false},
        {"name": "product_name", "type": "TEXT", "nullable": false, "primary_key": false},
        {"name": "quantity", "type": "INTEGER", "nullable": false, "primary_key": false}
      ],
      "foreign_keys": [
        {"column": "order_id", "references_table": "orders", "references_column": "id"}
      ]
    }
  ]
}
```

## Possible next steps

- Add scanners for Snowflake / BigQuery via their respective Python SDKs
- Push results into a search index (e.g., Elasticsearch) instead of a flat JSON file
- Add incremental scanning so only schema changes are re-collected
- Wrap the scanner as a packaged CLI binary for easy distribution to client environments

---

## 日本語

PostgreSQL や MySQL などのリレーショナルデータベースに接続し、テーブル・カラム・データ型・主キー・外部キーといったメタデータを自動で収集し、構造化されたJSON形式で出力する軽量なPythonツールです。

データカタログ製品が行っている「データソースをクロールしてスキーマの地図を作る」という仕組みを、シンプルに実装したプロジェクトです。誰かが手作業でドキュメントを作らなくても、データベースの中身を自動で把握できるようにすることを目指しています。

### 作った理由

企業の中には、どのデータベースにどんなデータがあるのか把握できていないケースが多くあります。データカタログ製品は、その課題を解決するために、各データソースを自動でスキャンしてメタデータを収集する「スキャナ」という仕組みを使っています。本プロジェクトは、その考え方を小規模に再現した実験的な実装です。データベース接続情報を渡すだけで、スキーマのスナップショットを取得し、カタログやインデックスに取り込める形で出力します。

### 主な機能

- PostgreSQL と MySQL の両方に対応(共通インターフェース `BaseScanner` を実装)
- 取得項目:スキーマ名、テーブル名、カラム名、データ型、NULL許容かどうか、主キー、外部キーの関係
- JSONファイルへの出力、およびターミナルでの読みやすいサマリー表示
- 新しいデータソースを追加する場合は、小さなクラスを1つ実装するだけで対応可能なモジュール設計
- セットアップ不要で動作確認できるSQLiteデモを同梱

### クイックデモ(データベース不要)

```bash
pip install -r requirements.txt
python demo.py
```

サンプルのSQLiteデータベース(`demo.db`)を作成し、自動でスキャンして、検出したスキーマを `metadata_output.json` に書き出します。

### 実際のデータベースに対して使う場合

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

### 出力例

```json
{
  "source": "sqlite",
  "scanned_at": "2026-06-30T07:57:00Z",
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

### 今後の改善案

- Snowflake / BigQuery など、クラウドデータウェアハウス向けスキャナの追加
- 結果をフラットなJSONではなく、Elasticsearch等の検索インデックスに直接投入できるようにする
- スキーマの差分のみを検出する増分スキャン機能の追加
- クライアント環境への配布を容易にするため、CLIをパッケージ化したバイナリとして提供
