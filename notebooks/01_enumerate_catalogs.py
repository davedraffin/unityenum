# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Enumerate Unity Catalog catalogs
# MAGIC
# MAGIC This notebook lists Unity Catalog catalogs and schemas and stores the inventory
# MAGIC as JSON for downstream notebooks.

# COMMAND ----------
import json
from pathlib import Path

from databricks.sdk import WorkspaceClient

from unity_docgen.catalogs import CatalogEnumerator

# COMMAND ----------
# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------
dbutils.widgets.text("inventory_output", "dbfs:/tmp/unity-docgen/catalogs.json")
dbutils.widgets.text("include_catalogs", "")
dbutils.widgets.text("exclude_catalogs", "")

# COMMAND ----------
output_path = dbutils.widgets.get("inventory_output")
include_catalogs = {
    name.strip() for name in dbutils.widgets.get("include_catalogs").split(",") if name.strip()
}
exclude_catalogs = {
    name.strip() for name in dbutils.widgets.get("exclude_catalogs").split(",") if name.strip()
}

# COMMAND ----------
client = WorkspaceClient()

enumerator = CatalogEnumerator(client)

catalogs = []
for catalog in enumerator.list_catalogs():
    if include_catalogs and catalog.name not in include_catalogs:
        continue
    if exclude_catalogs and catalog.name in exclude_catalogs:
        continue
    schemas = enumerator.list_schemas(catalog.name)
    catalogs.append(
        {
            "catalog": catalog.name,
            "comment": catalog.comment,
            "schemas": [
                {
                    "schema": schema.name,
                    "comment": schema.comment,
                }
                for schema in schemas
            ],
        }
    )

payload = {"catalogs": catalogs}

# COMMAND ----------
# MAGIC %md
# MAGIC ## Write inventory

# COMMAND ----------
output_file = Path(output_path.replace("dbfs:", "/dbfs"))
output_file.parent.mkdir(parents=True, exist_ok=True)
output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

print(f"Wrote catalog inventory to {output_path}")
