import sqlite3
from typing import List

from .base import BaseScanner, TableMetadata, ColumnMetadata, ForeignKeyMetadata


class SQLiteScanner(BaseScanner):
    """
    Scans a SQLite database. Used for the zero-setup demo so the project
    can be run end-to-end without needing a real Postgres/MySQL server.
    """

    source_name = "sqlite"

    def connect(self):
        self.connection = sqlite3.connect(self.connection_params["path"])

    def list_tables(self) -> List[TableMetadata]:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )
        tables = [TableMetadata(schema="main", name=row[0]) for row in cur.fetchall()]

        for table in tables:
            cur.execute(f"PRAGMA table_info({table.name});")
            for _, col_name, data_type, notnull, _, pk in cur.fetchall():
                table.columns.append(
                    ColumnMetadata(
                        name=col_name,
                        type=data_type,
                        nullable=(notnull == 0),
                        primary_key=bool(pk),
                    )
                )

            cur.execute(f"PRAGMA foreign_key_list({table.name});")
            for row in cur.fetchall():
                # row: id, seq, table, from, to, on_update, on_delete, match
                table.foreign_keys.append(
                    ForeignKeyMetadata(
                        column=row[3], references_table=row[2], references_column=row[4]
                    )
                )

        cur.close()
        return tables
