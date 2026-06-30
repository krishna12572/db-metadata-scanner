import json


def export_json(metadata: dict, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def print_summary(metadata: dict):
    print(f"Source: {metadata['source']}")
    print(f"Scanned at: {metadata['scanned_at']}")
    print(f"Tables found: {len(metadata['tables'])}\n")

    for table in metadata["tables"]:
        print(f"  {table['schema']}.{table['name']} ({len(table['columns'])} columns)")
        for col in table["columns"]:
            pk_marker = " [PK]" if col["primary_key"] else ""
            null_marker = "NULL" if col["nullable"] else "NOT NULL"
            print(f"    - {col['name']}: {col['type']} ({null_marker}){pk_marker}")
        for fk in table["foreign_keys"]:
            print(
                f"    -> FK: {fk['column']} references "
                f"{fk['references_table']}.{fk['references_column']}"
            )
        print()
