from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MarkdownPage:
    title: str
    summary: str | None
    rows: list[dict[str, str]]
    columns: list[str]

    def render(self) -> str:
        lines = [f"# {self.title}", ""]
        if self.summary:
            lines.extend([self.summary, ""])
        lines.append("## Permissions")
        lines.append("")
        header = " | ".join(["Principal"] + self.columns)
        divider = " | ".join(["---"] * (len(self.columns) + 1))
        lines.append(header)
        lines.append(divider)
        for row in self.rows:
            row_values = [row.get("principal", "")] + [row.get(col, "") for col in self.columns]
            lines.append(" | ".join(row_values))
        lines.append("")
        return "\n".join(lines)


def write_markdown_page(output_dir: Path, page: MarkdownPage) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_title = page.title.replace("/", "-")
    destination = output_dir / f"{safe_title}.md"
    destination.write_text(page.render(), encoding="utf-8")
    return destination
