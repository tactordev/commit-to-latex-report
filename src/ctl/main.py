import os, shutil, re, os, subprocess, argparse, tempfile, datetime, time
from .latex import Document
import stat
from pathlib import Path
import sys

def validate_date(date: str):
    try:
        dt = datetime.datetime.strptime(date, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return argparse.ArgumentTypeError("Invalid date format. Expected dd/mm/yyyy.")


def get_resource_path(relative_path: str) -> Path:
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent.parent / relative_path

def Main():
    global path
    temp_dir = None

    url = ""

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL of the git repository (required)", default=None)
    parser.add_argument("--start", type=validate_date, help="Start date for commits (dd/mm/yyyy)", default=None)
    parser.add_argument("--end", type=validate_date, help="End date for commits (dd/mm/yyyy)", default=None)
    parser.add_argument("--count", type=int, help="Number of commits to fetch in total", default=None)
    
    args = parser.parse_args()

    if args.url is not None and args.url.strip() != "":
        temp_dir = tempfile.mkdtemp(prefix="ctl-")
        path = os.path.join(temp_dir, "repo")

        print("Cloning repository...")
        url = args.url.strip()
        subprocess.run(["git", "clone", "--tags", args.url.strip(), "repo"], check=True, cwd=temp_dir)

    else:
        return print("No url provided in --url=https://github.com/author/repository.")

        
    git_cmd = [
        "git", "log", "--all", "--stat", "--source", "--date=iso-strict", 
        "--pretty=format:COMMIT_START%nhash:%H%nauthor:%an%ndate:%ai%nparents:%P%nrefs:%D%nsubject:%s%nbody:%b%nCOMMIT_END"
    ]

    if args.start:
        git_cmd.append(f"--since={args.start} 00:00:00")
    if args.end:
        git_cmd.append(f"--until={args.end} 23:59:59")
    else:
        today = datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")
    if args.count is not None:
        if args.count <= 0:
            return print("Error: --count must be a positive integer.")

        git_cmd.append(f"-n{args.count}")

        
    print("Running git log command...")
    out = subprocess.check_output(git_cmd, cwd=path)


    doc = Document()
    commits = parseLog(out, url)
    doc.add("table", commits['releases'], "New Releases")
    doc.add("table", commits['commits'], "Recent Commits")
    doc.add("table", commits['commits'], "Details")
    rendered = doc.render(
        summary_info=f"{len(commits['commits'])} commits, {len(set(commit['author_email'] for commit in commits['commits'].values()))} collaborator(s)",
        new_releases=doc.contents[0].render(),
        recent_commits=doc.contents[1].render(),
        details=doc.contents[2].render(),
    )

    temp_path = get_resource_path("ctl/out.tex")
    with open(temp_path, "w") as f:
        f.write(rendered)

    subprocess.run([
        "xelatex",
        "-interaction=nonstopmode",
        "out.tex",
    ], check=True, cwd="src/ctl")

    if not os.path.exists("src/ctl/out.pdf"):
        return print("PDF file not generated.")

    print("Cleaning up temporary files...")

    if temp_dir is not None:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("PDF file generated: file:///" + os.path.abspath("src/ctl/out.pdf"), "(CTRL + Click to open).")
    return


def parseLog(raw: bytes, url: str):
    raw = raw.decode("utf-8")


    print("Parsing git log output...")

    commits = {}
    releases = {}

    stat_re = re.compile(
        r"^\s*\d+ files? changed"
        r"(?:, (?P<insertions>\d+) insertions?\(\+\))?"
        r"(?:, (?P<deletions>\d+) deletions?\(-\))?\s*$",
        re.MULTILINE
    )   

    for chunk in raw.split("COMMIT_START\n"):
        chunk = chunk.strip()
        if not chunk:
            continue

        if "COMMIT_END" in chunk:
            metadata = chunk.split("COMMIT_END")[0]
        else:
            metadata = chunk

        stats_match = stat_re.search(chunk)
        insertions = int(stats_match.group("insertions")) if stats_match and stats_match.group("insertions") else 0
        deletions = int(stats_match.group("deletions")) if stats_match and stats_match.group("deletions") else 0

        fields = {
            "hash": None,
            "author": None,
            "date": None,
            "parents": None,
            "refs": None,
            "subject": None,
            "body": ""
        }

        body_lines = []
        in_body = False



        lines = metadata.splitlines()

        for line in lines:
            if in_body:
                body_lines.append(line)
            elif line.startswith("hash:"):
                fields["hash"] = line[5:].strip()
            elif line.startswith("author:"):
                fields["author"] = line[7:].strip()
            elif line.startswith("date:"):
                fields["date"] = line[5:].strip()
            elif line.startswith("parents:"):
                fields["parents"] = line[8:].strip()
            elif line.startswith("refs:"):
                fields["refs"] = line[5:].strip()
            elif line.startswith("subject:"):
                fields["subject"] = line[8:].strip()
            elif line.startswith("body:"):
                in_body = True
                first_body_line = line[5:].strip()
                if first_body_line:
                    body_lines.append(first_body_line)

        commit_hash = fields["hash"]
        if not commit_hash:
            continue

        date_str = fields["date"]
        formatted_date = None
        if date_str:
            try:
                dt = datetime.datetime.fromisoformat(date_str)
                formatted_date = f"{dt.date()} {dt.time()}"
            except ValueError:
                formatted_date = date_str

        parent_raw = fields["parents"]
        formatted_parents = None
        if parent_raw:
            formatted_parents = " ".join([p[:7] for p in parent_raw.split()])

        refs_str = fields["refs"] or ""
        branch = None
        tags = []

        if refs_str:
            for ref in refs_str.split(","):
                ref = ref.strip()
                if ref.startswith("tag:"):
                    tags.append(ref[4:].strip())
                elif "->" in ref:
                    branch = ref.split("->")[1].strip()
                elif ref and not branch and not ref.startswith("origin/"):
                    branch = ref

        description = "\n".join(body_lines).strip()
        if description:
            description = (description
                           .replace("&", "\\&")
                           .replace("_", "\\_")
                           .replace("%", "\\%")
                           .replace("#", "\\#"))
            description = description.replace("\n", " \\\\ ")

        title = fields["subject"]
        if title:
            title = (title
                     .replace("&", "\\&")
                     .replace("_", "\\_")
                     .replace("%", "\\%")
                     .replace("#", "\\#"))

        commits[commit_hash] = {
            "hash": commit_hash,
            "title": title,
            "author_name": fields["author"],
            "author_email": None,  
            "date": formatted_date,
            "lines_changed": insertions + deletions,
            "insertions": insertions,
            "deletions": deletions,
            "branch": branch,
            "parent_id": formatted_parents if formatted_parents else "N/A",
            "description": description if description else "N/A",
            "repo_url": url
        }

        for tag_name in tags:
            releases[tag_name] = {
                "hash": commit_hash[:7],
                "tag": tag_name,
                "title": title,
                "author_name": fields["author"],
                "author_email": None,
                "date": formatted_date,
                "repo_url": url
            }

    return {'commits': commits, 'releases': releases}