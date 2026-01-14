# Unity Catalog Permissions Doc Generator

This repository provides a Databricks notebook-driven workflow that enumerates Unity Catalog
entities, captures their permissions, and generates Markdown documentation in a structured tree
for review through an Azure DevOps pull request.

The notebooks are designed to run on serverless Databricks clusters using a managed identity or
service principal that has read access to Unity Catalog metadata and grants.

## Workflow overview

1. **Enumerate catalogs**: list all catalogs in the lakehouse and persist the catalog inventory.
2. **Crawl permissions**: walk catalogs → schemas → tables, volumes, UDFs, and models while
   collecting descriptions and privilege assignments for each entity.
3. **Generate Markdown**: produce one Markdown page per entity (catalog, schema, table, volume,
   UDF, or model) with a summary and a permissions matrix.
4. **Publish documentation**: create a new branch in the Git-backed Databricks workspace folder
   and open a pull request for manual review.

## Repository layout

- `notebooks/`: Databricks notebooks orchestrating the workflow.
- `src/unity_docgen/`: Reusable helpers for enumeration, permission mapping, Markdown formatting,
  and Azure DevOps PR creation.
- `resources/`: Databricks job definition used by the pipeline.
- `config/`: Example configuration for workspace paths, repo URLs, and privilege matrix layout.

## Configuration

Copy `config/example_config.yaml` and update the values for your workspace, Azure DevOps repo,
and Unity Catalog targets.

## Running in Databricks

1. Import the notebooks into the target workspace.
2. Create a job from `resources/databricks_job.yml` (or use Databricks Asset Bundles).
3. Provide configuration values via widgets or environment variables as documented in the
   notebooks.

## Outputs

- Markdown documentation stored in a Git-backed workspace directory.
- A pull request in Azure DevOps containing the updated documentation.
