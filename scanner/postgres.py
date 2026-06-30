from typing import List

from .base import BaseScanner, TableMetadata, ColumnMetadata, ForeignKeyMetadata


class PostgresScanner(BaseScanner):
    """Scans a PostgreSQL database and collects table/column metadata."""

    source_name = "postgres"

    def connect(self):
        import psycopg2

        self.connection = psycopg2.connect(
            host=self.connection_params["host"],
            port=self.connection_params.get("port", 5432),
            dbname=self.connection_params["dbname"],
            user=self.connection_params["user"],
            password=self.connection_params["password"],
        )

    def list_tables(self) -> List[TableMetadata]:
        cur = self.connection.cursor()

        cur.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name;
            """
        )
        tables = [TableMetadata(schema=s, name=n) for s, n in cur.fetchall()]

        for table in tables:
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position;
                """,
                (table.schema, table.name),
            )
            pk_columns = self._primary_key_columns(cur, table.schema, table.name)

            for col_name, data_type, is_nullable in cur.fetchall():
                table.columns.append(
                    ColumnMetadata(
                        name=col_name,
                        type=data_type,
                        nullable=(is_nullable == "YES"),
                        primary_key=col_name in pk_columns,
                    )
                )

            table.foreign_keys = self._foreign_keys(cur, table.schema, table.name)

        cur.close()
        return tables

    @staticmethod
    def _primary_key_columns(cur, schema: str, table: str):
        cur.execute(
            """
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = %s AND tc.table_name = %s;
            """,
            (schema, table),
        )
        return {row[0] for row in cur.fetchall()}

    @staticmethod
    def _foreign_keys(cur, schema: str, table: str) -> List[ForeignKeyMetadata]:
        cur.execute(
            """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = %s AND tc.table_name = %s;
            """,
            (schema, table),
        )
        return [
            ForeignKeyMetadata(
                column=col, references_table=ref_table, references_column=ref_col
            )
            for col, ref_table, ref_col in cur.fetchall()
        ]
