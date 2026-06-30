from typing import List

from .base import BaseScanner, TableMetadata, ColumnMetadata, ForeignKeyMetadata


class MySQLScanner(BaseScanner):
    """Scans a MySQL database and collects table/column metadata."""

    source_name = "mysql"

    def connect(self):
        import pymysql

        self.connection = pymysql.connect(
            host=self.connection_params["host"],
            port=self.connection_params.get("port", 3306),
            db=self.connection_params["dbname"],
            user=self.connection_params["user"],
            password=self.connection_params["password"],
        )

    def list_tables(self) -> List[TableMetadata]:
        cur = self.connection.cursor()
        dbname = self.connection_params["dbname"]

        cur.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            ORDER BY table_name;
            """,
            (dbname,),
        )
        tables = [TableMetadata(schema=s, name=n) for s, n in cur.fetchall()]

        for table in tables:
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable, column_key
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position;
                """,
                (dbname, table.name),
            )
            for col_name, data_type, is_nullable, column_key in cur.fetchall():
                table.columns.append(
                    ColumnMetadata(
                        name=col_name,
                        type=data_type,
                        nullable=(is_nullable == "YES"),
                        primary_key=(column_key == "PRI"),
                    )
                )

            table.foreign_keys = self._foreign_keys(cur, dbname, table.name)

        cur.close()
        return tables

    @staticmethod
    def _foreign_keys(cur, dbname: str, table: str) -> List[ForeignKeyMetadata]:
        cur.execute(
            """
            SELECT column_name, referenced_table_name, referenced_column_name
            FROM information_schema.key_column_usage
            WHERE table_schema = %s AND table_name = %s
              AND referenced_table_name IS NOT NULL;
            """,
            (dbname, table),
        )
        return [
            ForeignKeyMetadata(
                column=col, references_table=ref_table, references_column=ref_col
            )
            for col, ref_table, ref_col in cur.fetchall()
        ]
