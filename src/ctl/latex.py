MAX_ROWS_ON_PAGE = 25


class Document:
    def __init__(self):
        self.contents = []
        self.definitions = []
        self.packages = ["hyperref", "xcolor", "tabularx", "booktabs"]

    def add(self, type, content, table_type: str | None = None):
        match type:
            case "table":
                self.contents.append(
                    Table(self, content, table_type)
                )
                return

            case _:
                raise ValueError(f"Unknown type: {type}")


    def render(self):
        base = ""
        with open("src/ctl/report_format.txt", "r") as f:
            base = f.readlines()

        base = "".join(base)

        return base


class Table:
    def __init__(self, document: Document, content: dict, type: str | None = None):
        self.document = document
        self.content = content
        self.type = type

    def render(self):
        def clean(val):
            if val is None:
                return ""
            val = str(val)
            return val.replace("&", "\\&").replace("_", "\\_").replace("%", "\\%").replace("#", "\\#")

        match (self.type):
            case "New Releases":
                rows = []
                for commit in self.content.values():
                    commit_hash = clean(commit['hash'][:7])
                    tag_name = clean(commit.get('tag') or '')
                    title = clean(commit['title'])
                    if len(title) > 20:
                        title = f"{title[:20]}..."
                    author = clean(commit['author_name'])
                    date = clean(commit['date'])
                    verified = '\\checkmark' if commit.get('verified') else '\\xmark'
                    rows.append(f"{commit_hash} & {tag_name} & {title} & {author} & {date} & {verified} \\\\ \\hline\n")

                template = f"""#[\\small {len(self.content.keys())} new release{"s" if len(self.content.keys()) != 1 else ""}.]#
\\noindent
\\begin#[table]#-(h)-
\\centering
\\begin#[tabularx]##[\\textwidth]##[lllllc]#
\\textbf#[Commit]# & \\textbf#[Tag]# & \\textbf#[Title]# & \\textbf#[Author]# & \\textbf#[Date]# & \\textbf#[Verified]# \\\\ \\midrule
""" + "".join(rows) + """\\bottomrule
\\end#[tabularx]#
\\end#[table]#"""
                return template.replace("#[", "{").replace("]#", "}").replace("-(", "[").replace(")-", "]")

            case "Recent Commits":
                num_rows_before = 2
                for content in self.document.contents:
                    if isinstance(content, Table) and (content.type == "Recent Commits" or content.type == "Details"):
                        break
                    num_rows_before += len(content.content)

                rows_to_show = MAX_ROWS_ON_PAGE - num_rows_before
                remaining_rows = len(self.content.keys()) - rows_to_show

                rows = []
                for commit in list(self.content.values())[:rows_to_show]:
                    commit_hash = clean(commit['hash'][:7])
                    title = clean(commit['title'])
                    if len(title) > 20:
                        title = f"{title[:20]}..."
                    author = clean(commit['author_name'])
                    date = clean(commit['date'])
                    insertions = commit.get('insertions', 0)
                    deletions = commit.get('deletions', 0)
                    rows.append(f"{commit_hash} & {title} & {author} & {date} & \\textcolor#[insertion]##[+{insertions}]# \\textcolor#[deletion]##[-{deletions}]# \\\\ \\hline\n")

                template = f"""\n\n\n#[\\small {len(self.content.keys())} recent commit{"s" if len(self.content.keys()) != 1 else ""}]#
\\noindent
\\begin#[table]#-(h)-
\\centering
\\begin#[tabularx]##[\\textwidth]##[llllc]#
\\textbf#[id]# & \\textbf#[Title]# & \\textbf#[Author]# & \\textbf#[Date]# & \\textbf#[changes]# \\\\ \\midrule
{"".join(rows)}\\bottomrule
\\end#[tabularx]#
\\end#[table]#
"""
                rendered = template.replace("#[", "{").replace("]#", "}").replace("-(", "[").replace(")-", "]")
                if remaining_rows > 0:
                    rendered += f"\\textit#[{remaining_rows} commit{'s' if remaining_rows != 1 else ''} not shown]#\n".replace("#[", "{").replace("]#", "}")
                return rendered

            case "Details":
                rendered = ""
                lastCleared = 0
                for commit in self.content.values():
                    commit_hash = clean(commit['hash'])
                    title = clean(commit['title'])
                    lines_changed = clean(commit.get('lines_changed', 0))
                    branch = clean(commit.get('branch') or 'N/A')
                    parent_id = clean(commit.get('parent_id') or 'N/A')
                    author = clean(commit['author_name'])
                    insertions = clean(commit.get('insertions', 0))
                    deletions = clean(commit.get('deletions', 0))
                    description = commit.get('description', '')

                    split_description = ""
                    for count, char in enumerate(description):
                        split_description += char
                        if count % 80 == 0 and count != 0:
                            split_description += "\n"
                    rendered += f"""
\\begin#[table]#-(h)-
\\centering
\\begin#[tabularx]##[\\textwidth]##[|l|l|l|l|l|l|l|l|l|l|]#
\\hline
\\multicolumn#[10]##[|l|]##[{commit['title']}]# \\\\
\\hline \\multicolumn#[6]##[|l|]##[{commit['hash']} \hspace#[3.75cm]# ]# & \\multicolumn#[4]##[c|]##[0 lines changed]# \\\\
\\hline \\multicolumn#[2]##[|l|]##[{commit['branch']}]# \hfill & \\multicolumn#[2]##[|l|]##[{commit['parent_id'][:40] if commit['parent_id'] and len(commit['parent_id']) > 40 else commit['parent_id'] or 'N/A'}]# & \\multicolumn#[2]##[|l|]##[{commit['author_name']}]# & \\multicolumn#[2]##[|c|]##[\\textcolor#[insertion]##[+{insertions}]#]# & \\multicolumn#[2]##[|c|]##[\\textcolor#[deletion]##[-{deletions}]#]# \\\\
\\hline \\multicolumn#[10]##[|l|]##[{description}]# \\\\
\\hline
\\end#[tabularx]#

\\end#[table]#
""".replace("#[", "{").replace("]#", "}").replace("-(", "[").replace(")-", "]")
                    if lastCleared > 6:
                        rendered += "\\clearpage\n"
                        lastCleared = 0
                    else:
                        lastCleared += 1
                return rendered

            case _: 
                raise ValueError(f"Unknown table type: {self.type}")