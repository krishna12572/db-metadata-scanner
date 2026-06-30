"""
CLI entrypoint to scan a real PostgreSQL or MySQL database.

Example:
    python main.py --engine postgres --host localhost --port 5432 \
        --dbname mydb --user myuser --password mypass \
        --output metadata_output.json
"""
import argparse

from scanner.exporter import export_json, print_summary


def build_scanner(args):
    if args.engine == "postgres":
        from scanner.postgres import PostgresScanner

        return PostgresScanner(
            host=args.host,
            port=args.port,
            dbname=args.dbname,
            user=args.user,
            password=args.password,
        )
    elif args.engine == "mysql":
        from scanner.mysql import MySQLScanner

        return MySQLScanner(
            host=args.host,
            port=args.port,
            dbname=args.dbname,
            user=args.user,
            password=args.password,
        )
    else:
        raise ValueError(f"Unsupported engine: {args.engine}")


def parse_args():
    parser = argparse.ArgumentParser(description="Scan a database and export its metadata.")
    parser.add_argument("--engine", choices=["postgres", "mysql"], required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--dbname", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--output", default="metadata_output.json")
    return parser.parse_args()


def main():
    args = parse_args()
    scanner = build_scanner(args)

    print(f"Connecting to {args.engine} database '{args.dbname}' at {args.host}...\n")
    metadata = scanner.scan()

    print_summary(metadata)
    export_json(metadata, args.output)
    print(f"Metadata written to {args.output}")


if __name__ == "__main__":
    main()
