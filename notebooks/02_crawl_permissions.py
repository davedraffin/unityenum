# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Crawl Unity Catalog permissions
# MAGIC
# MAGIC Reads the catalog inventory and retrieves privilege assignments for each entity.

# COMMAND ----------
import json
from pathlib import Path

from databricks.sdk import WorkspaceClient

from unity_docgen.catalogs import CatalogEnumerator
from unity_docgen.permissions import fetch_permissions, securable_type_for_kind

# COMMAND ----------
# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------
dbutils.widgets.text("inventory_input", "dbfs:/tmp/unity-docgen/catalogs.json")
dbutils.widgets.text("permissions_output", "dbfs:/tmp/unity-docgen/permissions.json")

# COMMAND ----------
inventory_path = dbutils.widgets.get("inventory_input")
permissions_path = dbutils.widgets.get("permissions_output")

# COMMAND ----------
client = WorkspaceClient()

enumerator = CatalogEnumerator(client)

inventory_file = Path(inventory_path.replace("dbfs:", "/dbfs"))
inventory = json.loads(inventory_file.read_text(encoding="utf-8"))

entries: list[dict[str, object]] = []

for catalog in inventory["catalogs"]:
    catalog_name = catalog["catalog"]
    catalog_full_name = catalog_name
    entries.append(
        {
            "full_name": catalog_full_name,
            "kind": "catalog",
            "comment": catalog.get("comment"),
            "permissions": [
                {
                    "principal": entry.principal,
                    "privileges": sorted(entry.privileges),
                }
                for entry in fetch_permissions(client, securable_type_for_kind("catalog"), catalog_full_name)
            ],
        }
    )
    for schema in catalog["schemas"]:
        schema_name = schema["schema"]
        schema_full_name = f"{catalog_name}.{schema_name}"
        entries.append(
            {
                "full_name": schema_full_name,
                "kind": "schema",
                "comment": schema.get("comment"),
                "permissions": [
                    {
                        "principal": entry.principal,
                        "privileges": sorted(entry.privileges),
                    }
                    for entry in fetch_permissions(client, securable_type_for_kind("schema"), schema_full_name)
                ],
            }
        )

        for entity in enumerator.list_schema_entities(catalog_name, schema_name):
            entity_full_name = f"{catalog_name}.{schema_name}.{entity.name}"
            entries.append(
                {
                    "full_name": entity_full_name,
                    "kind": entity.kind,
                    "catalog": catalog_name,
                    "schema": schema_name,
                    "comment": entity.comment,
                    "permissions": [
                        {
                            "principal": entry.principal,
                            "privileges": sorted(entry.privileges),
                        }
                        for entry in fetch_permissions(
                            client,
                            securable_type_for_kind(entity.kind),
                            entity_full_name,
                        )
                    ],
                }
            )

payload = {"entities": entries}

# COMMAND ----------
# MAGIC %md
# MAGIC ## Write permissions inventory

# COMMAND ----------
permissions_file = Path(permissions_path.replace("dbfs:", "/dbfs"))
permissions_file.parent.mkdir(parents=True, exist_ok=True)
permissions_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

print(f"Wrote permissions inventory to {permissions_path}")
