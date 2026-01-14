from dataclasses import dataclass

from databricks.sdk import WorkspaceClient


@dataclass(frozen=True)
class PermissionEntry:
    principal: str
    privileges: set[str]


def fetch_permissions(
    client: WorkspaceClient,
    securable_type: str,
    full_name: str,
) -> list[PermissionEntry]:
    """Fetch privileges for a securable (catalog, schema, table, volume, etc.)."""
    grants = client.grants.get(securable_type=securable_type, full_name=full_name)
    entries = []
    for privilege_assignment in grants.privilege_assignments or []:
        entries.append(
            PermissionEntry(
                principal=privilege_assignment.principal,
                privileges=set(privilege_assignment.privileges or []),
            )
        )
    return entries


def securable_type_for_kind(kind: str) -> str:
    """Map catalog entity kinds to Unity Catalog securable types."""
    mapping = {
        "catalog": "CATALOG",
        "schema": "SCHEMA",
        "table": "TABLE",
        "volume": "VOLUME",
        "udf": "FUNCTION",
        "function": "FUNCTION",
        "model": "REGISTERED_MODEL",
    }
    return mapping.get(kind.lower(), kind.upper())


def build_privilege_matrix(
    permissions: list[PermissionEntry],
    columns: list[str],
) -> list[dict[str, str]]:
    """Return rows for Markdown rendering.

    Each row contains the principal followed by a column per privilege.
    """
    rows: list[dict[str, str]] = []
    for entry in permissions:
        row = {"principal": entry.principal}
        for column in columns:
            row[column] = "X" if column in entry.privileges else ""
        rows.append(row)
    return rows
