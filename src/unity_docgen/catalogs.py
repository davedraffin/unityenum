from dataclasses import dataclass
from typing import Iterable

from databricks.sdk import WorkspaceClient


@dataclass(frozen=True)
class CatalogRef:
    name: str
    comment: str | None


@dataclass(frozen=True)
class SchemaRef:
    catalog: str
    name: str
    comment: str | None


@dataclass(frozen=True)
class EntityRef:
    catalog: str
    schema: str | None
    name: str
    kind: str
    comment: str | None


class CatalogEnumerator:
    """Enumerate Unity Catalog catalogs and schemas using the Databricks SDK."""

    def __init__(self, client: WorkspaceClient) -> None:
        self._client = client

    def list_catalogs(self) -> list[CatalogRef]:
        catalogs = []
        for catalog in self._client.catalogs.list():
            catalogs.append(CatalogRef(name=catalog.name, comment=catalog.comment))
        return catalogs

    def list_schemas(self, catalog_name: str) -> list[SchemaRef]:
        schemas = []
        for schema in self._client.schemas.list(catalog_name):
            schemas.append(
                SchemaRef(
                    catalog=catalog_name,
                    name=schema.name,
                    comment=schema.comment,
                )
            )
        return schemas

    def list_tables(self, catalog_name: str, schema_name: str) -> list[EntityRef]:
        return [
            EntityRef(
                catalog=catalog_name,
                schema=schema_name,
                name=table.name,
                kind="table",
                comment=table.comment,
            )
            for table in self._client.tables.list(catalog_name, schema_name)
        ]

    def list_functions(self, catalog_name: str, schema_name: str) -> list[EntityRef]:
        return [
            EntityRef(
                catalog=catalog_name,
                schema=schema_name,
                name=function.name,
                kind="udf",
                comment=function.comment,
            )
            for function in self._client.functions.list(catalog_name, schema_name)
        ]

    def list_models(self, catalog_name: str, schema_name: str) -> list[EntityRef]:
        return [
            EntityRef(
                catalog=catalog_name,
                schema=schema_name,
                name=model.name,
                kind="model",
                comment=model.comment,
            )
            for model in self._client.registered_models.list(catalog_name, schema_name)
        ]

    def list_volumes(self, catalog_name: str, schema_name: str) -> list[EntityRef]:
        return [
            EntityRef(
                catalog=catalog_name,
                schema=schema_name,
                name=volume.name,
                kind="volume",
                comment=volume.comment,
            )
            for volume in self._client.volumes.list(catalog_name, schema_name)
        ]

    def list_schema_entities(self, catalog_name: str, schema_name: str) -> Iterable[EntityRef]:
        yield from self.list_tables(catalog_name, schema_name)
        yield from self.list_volumes(catalog_name, schema_name)
        yield from self.list_functions(catalog_name, schema_name)
        yield from self.list_models(catalog_name, schema_name)
