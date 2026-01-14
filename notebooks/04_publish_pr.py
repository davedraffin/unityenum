# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Publish documentation and open PR
# MAGIC
# MAGIC Creates a new branch, commits the documentation, and opens a pull request in
# MAGIC Azure DevOps. Adjust the Git remote to match your workspace-backed repo.

# COMMAND ----------
import subprocess
from datetime import datetime

from unity_docgen.azure_devops import build_pr_details

# COMMAND ----------
# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------
dbutils.widgets.text("docs_repo_path", "/Workspace/Repos/your-org/unity-catalog-docs")
dbutils.widgets.text("branch_prefix", "unity-docs")
dbutils.widgets.text("reviewers", "admin-team@your-org.com")

# COMMAND ----------
docs_repo_path = dbutils.widgets.get("docs_repo_path")
branch_prefix = dbutils.widgets.get("branch_prefix")
reviewers = [reviewer.strip() for reviewer in dbutils.widgets.get("reviewers").split(",")]

# COMMAND ----------
run_name = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
branch_name = f"{branch_prefix}/{run_name}"

subprocess.run(["git", "-C", docs_repo_path, "checkout", "-b", branch_name], check=True)
subprocess.run(["git", "-C", docs_repo_path, "add", "docs"], check=True)
subprocess.run(
    ["git", "-C", docs_repo_path, "commit", "-m", "Update Unity Catalog docs"],
    check=True,
)
subprocess.run(["git", "-C", docs_repo_path, "push", "-u", "origin", branch_name], check=True)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Create Azure DevOps PR

# COMMAND ----------
pr_details = build_pr_details(run_name, reviewers)

print("Create the pull request in Azure DevOps using the details below:")
print(pr_details)
