# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Generate Markdown documentation
# MAGIC
# MAGIC Converts the permissions inventory into Markdown pages stored in a Git-backed
# MAGIC Databricks workspace directory.

# COMMAND ----------
import json
from pathlib import Path

from unity_docgen.markdown import MarkdownPage, write_markdown_page
from unity_docgen.permissions import PermissionEntry, build_privilege_matrix

# COMMAND ----------
# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------
dbutils.widgets.text("permissions_input", "dbfs:/tmp/unity-docgen/permissions.json")
dbutils.widgets.text("docs_output", "/Workspace/Repos/your-org/unity-catalog-docs/docs/unity-catalog")
dbutils.widgets.text(
    "privilege_columns",
    "ALL PRIVILEGES,ACCESS,APPLY TAG,BROWSE,CREATE CATALOG,CREATE CLEAN ROOM,CREATE CONNECTION,"
    "CREATE EXTERNAL LOCATION,CREATE EXTERNAL METADATA,CREATE EXTERNAL TABLE,CREATE EXTERNAL VOLUME,"
    "CREATE FOREIGN CATALOG,CREATE FOREIGN SECURABLE,CREATE FUNCTION,CREATE MANAGED STORAGE,"
    "CREATE MATERIALIZED VIEW,CREATE MODEL,CREATE MODEL VERSION,CREATE PROVIDER,CREATE RECIPIENT,"
    "CREATE SCHEMA,CREATE SERVICE CREDENTIAL,CREATE SHARE,CREATE STORAGE CREDENTIAL,CREATE TABLE,"
    "CREATE VOLUME,EXECUTE,EXECUTE CLEAN ROOM TASK,EXTERNAL USE LOCATION,EXTERNAL USE SCHEMA,"
    "MANAGE,MODIFY,MODIFY CLEAN ROOM,READ FILES,READ VOLUME,REFRESH,SELECT,SET SHARE PERMISSION,"
    "USE CATALOG,USE CONNECTION,USE MARKETPLACE ASSETS,USE PROVIDER,USE RECIPIENT,USE SCHEMA,"
    "USE SHARE,WRITE FILES,WRITE VOLUME",
)

# COMMAND ----------
permissions_input = dbutils.widgets.get("permissions_input")
docs_output = dbutils.widgets.get("docs_output")
privilege_columns = [column.strip() for column in dbutils.widgets.get("privilege_columns").split(",")]

# COMMAND ----------
permissions_file = Path(permissions_input.replace("dbfs:", "/dbfs"))
permissions = json.loads(permissions_file.read_text(encoding="utf-8"))

output_dir = Path(docs_output)

# COMMAND ----------
for entity in permissions["entities"]:
    permissions_entries = [
        PermissionEntry(principal=entry["principal"], privileges=set(entry["privileges"]))
        for entry in entity["permissions"]
    ]
    rows = build_privilege_matrix(permissions_entries, privilege_columns)

    if entity["kind"] == "catalog":
        title = f"Catalogs - {entity['full_name']}"
    elif entity["kind"] == "schema":
        title = f"Schemas - {entity['full_name']}"
    elif entity["kind"] == "table":
        title = f"Tables - {entity['full_name']}"
    elif entity["kind"] == "volume":
        title = f"Volumes - {entity['full_name']}"
    elif entity["kind"] == "udf":
        title = f"UDFs - {entity['full_name']}"
    elif entity["kind"] == "model":
        title = f"Models - {entity['full_name']}"
    else:
        title = f"Entities - {entity['full_name']}"

    page = MarkdownPage(
        title=title,
        summary=entity.get("comment"),
        rows=rows,
        columns=privilege_columns,
    )

    write_markdown_page(output_dir, page)

print(f"Wrote documentation to {docs_output}")
