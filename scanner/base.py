from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class ColumnMetadata:
    name: str
    type: str
    nullable: bool
    primary_key: bool = False


@dataclass
class ForeignKeyMetadata:
    column: str
    references_table: str
    references_column: str


@dataclass
class TableMetadata:
    schema: str
    name: str
    columns: List[ColumnMetadata] = field(default_factory=list)
    foreign_keys: List[ForeignKeyMetadata] = field(default_factory=list)


class BaseScanner(ABC):
    """
    Common interface every data source scanner must implement.

    Adding support for a new database engine means subclassing this and
    implementing `connect()` and `list_tables()` — the rest of the
    pipeline (export, summary printing) stays the same.
    """

    source_name: str = "base"

    def __init__(self, **connection_params):
        self.connection_params = connection_params
        self.connection = None

    @abstractmethod
    def connect(self):
        """Open a connection to the data source."""
        raise NotImplementedError

    @abstractmethod
    def list_tables(self) -> List[TableMetadata]:
        """Return metadata for every table the scanner can see."""
        raise NotImplementedError

    def close(self):
        if self.connection is not None:
            self.connection.close()

    def scan(self) -> dict:
        """Run the full scan and return a JSON-serializable result."""
        self.connect()
        try:
            tables = self.list_tables()
        finally:
            self.close()

        return {
            "source": self.source_name,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "tables": [
                {
                    "schema": t.schema,
                    "name": t.name,
                    "columns": [
                        {
                            "name": c.name,
                            "type": c.type,
                            "nullable": c.nullable,
                            "primary_key": c.primary_key,
                        }
                        for c in t.columns
                    ],
                    "foreign_keys": [
                        {
                            "column": fk.column,
                            "references_table": fk.references_table,
                            "references_column": fk.references_column,
                        }
                        for fk in t.foreign_keys
                    ],
                }
                for t in tables
            ],
        }
