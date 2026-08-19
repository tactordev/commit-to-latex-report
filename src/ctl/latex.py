from pathlib import Path

from jinja2 import Environment, FileSystemLoader


MAX_ROWS_ON_PAGE = 25
TEMPLATE_DIR = Path(__file__).resolve().parent


def escape_latex(value):
    if value is None:
        return ""

    value = str(value)
    return (
        value.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("_", r"\_")
        .replace("%", r"\%")
        .replace("#", r"\#")
    )


class TemplateRenderer:
    def __init__(self):
        self.environment = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            variable_start_string="[[",
            variable_end_string="]]",
            block_start_string="[%",
            block_end_string="%]",
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.environment.filters["latex"] = escape_latex

    def render(self, template_name: str, **context):
        template = self.environment.get_template(template_name)
        return template.render(**context)


class Document:
    def __init__(self):
        self.contents = []
        self.definitions = []
        self.packages = ["hyperref", "xcolor", "tabularx", "booktabs"]
        self.renderer = TemplateRenderer()

    def add(self, type, content, table_type: str | None = None):
        match type:
            case "table":
                self.contents.append(Table(self, content, table_type))
                return
            case _:
                raise ValueError(f"Unknown type: {type}")

    def render(self, **context):
        return self.renderer.render("report_format.txt", **context)

def format_parent(parent):
    if not parent:
        return "N/A"
    
    return " ".join([p[:7] for p in parent.split()])

class Table:
    def __init__(self, document: Document, content: dict, type: str | None = None):
        self.document = document
        self.content = content
        self.type = type

    def render(self):
        match self.type:
            case "New Releases":
                rows = []
                for commit in self.content.values():
                    rows.append(
                        {
                            "hash": commit["hash"],
                            "short_hash": commit["hash"][:7],
                            "tag_name": commit.get("tag") or "",
                            "title": commit["title"],
                            "author": commit["author_name"],
                            "date": commit["date"],
                            "verified": True,
                            "commit_url": f"{commit["repo_url"]}/commit/{commit["hash"]}"
                        }
                    )

                return self.document.renderer.render(
                    "table_new_releases.txt",
                    count=len(self.content),
                    rows=rows,
                )

            case "Recent Commits":
                num_rows_before = 2
                for content in self.document.contents:
                    if isinstance(content, Table) and content.type in ("Recent Commits", "Details"):
                        break
                    num_rows_before += len(content.content)

                rows_to_show = MAX_ROWS_ON_PAGE - num_rows_before
                remaining_rows = len(self.content) - rows_to_show
                rows = []

                for commit in list(self.content.values())[:rows_to_show]:
                    rows.append(
                        {
                            "commit_hash": commit["hash"][:7],
                            "title": f"{commit["title"][:20]}..." if len(commit["title"]) > 20 else commit["title"],
                            "author": commit["author_name"],
                            "date": commit["date"],
                            "insertions": commit.get("insertions", 0),
                            "deletions": commit.get("deletions", 0),
                        }
                    )

                return self.document.renderer.render(
                    "table_recent_commits.txt",
                    count=len(self.content),
                    rows=rows,
                    remaining_rows=remaining_rows,
                )

            case "Details":
                rows = []
                for commit in self.content.values():
                    rows.append(
                        {
                            "title": commit["title"],
                            "hash": commit["hash"],
                            "short_hash": commit["hash"][:7],
                            "commit_url": f"{commit["repo_url"]}/commit/{commit["hash"]}",
                            "branch": commit.get("branch") or "main",
                            "parent_id": format_parent(commit.get("parent_id")),
                            "author_name": commit["author_name"],
                            "insertions": commit.get("insertions", 0),
                            "deletions": commit.get("deletions", 0),
                            "description": commit.get("description", "N/A"),
                        }
                    )

                return self.document.renderer.render(
                    "table_details.txt",
                    rows=rows,
                    clearpage_after=15,
                )

            case _:
                raise ValueError(f"Unknown table type: {self.type}")