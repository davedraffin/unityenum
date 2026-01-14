from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PullRequestDetails:
    title: str
    description: str
    source_branch: str
    target_branch: str
    reviewers: list[str]


def build_pr_details(run_name: str, reviewers: list[str]) -> PullRequestDetails:
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    title = f"Unity Catalog documentation update ({run_name})"
    description = (
        "Automated Unity Catalog permission documentation update.\n"
        f"Run timestamp (UTC): {timestamp}."
    )
    source_branch = f"docs/{run_name}"
    return PullRequestDetails(
        title=title,
        description=description,
        source_branch=source_branch,
        target_branch="main",
        reviewers=reviewers,
    )
