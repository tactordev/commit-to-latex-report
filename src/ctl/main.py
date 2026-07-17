import os, shutil, re, os, subprocess, argparse, tempfile, datetime, time
from .latex import Document


import stat
from pathlib import Path
def readonly_to_writable(foo, file, err):
  if Path(file).suffix in ['.idx', '.pack'] and 'PermissionError' == err[0].__name__:
    os.chmod(file, stat.S_IWRITE)
    foo(file)



def Main():
    global path
    temp_dir = None

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the git repository", nargs="?")
    parser.add_argument("--url", help="URL of the git repository (optional)", default=None)
    args = parser.parse_args()

    if args.url is not None and args.url.strip() != "":
        temp_dir = tempfile.mkdtemp(prefix="ctl-")
        path = os.path.join(temp_dir, "repo")

        print("Cloning repository...")
        subprocess.run(["git", "clone", args.url.strip(), "repo"], check=True, cwd=temp_dir)

    else:
        path = args.path

    print("Running git log command...")
    out = subprocess.check_output([
        "git", "log", "--all", "--stat", "--source", "--date=iso-strict", 
        "--pretty=format:@@COMMIT@@%n%H%n%s%n%an%n%ae%n%ad%n%S%nParents: %P%nDescription: %b"
    ], cwd=path)


    doc = Document()
    commits = parseLog(out)
    doc.add("table", commits['releases'], "New Releases")
    doc.add("table", commits['commits'], "Recent Commits")
    doc.add("table", commits['commits'], "Details")
    rendered = doc.render()
    rendered = rendered.replace("[summary-info]", f"{len(commits['commits'])} commits, {len(set(commit['author_email'] for commit in commits['commits'].values()))} collaborator(s)")
    rendered = rendered.replace("[new-releases]", doc.contents[0].render())
    rendered = rendered.replace("[recent-commits]", doc.contents[1].render())
    rendered = rendered.replace("[details]", doc.contents[2].render())


    with open("src/ctl/out.tex", "w") as f:
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


def parseLog(raw: bytes):
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

    for chunk in re.compile(r"^@@COMMIT@@$", re.MULTILINE).split(raw):
        chunk = chunk.strip("\n")
        if not chunk.strip():
            continue

        stats_match = stat_re.search(chunk)
        if stats_match:
            metadata_part = chunk[:stats_match.start()]
        else:
            metadata_part = chunk

        lines = metadata_part.strip().split("\n")


        hash = lines[0].strip() if len(lines) > 0 else None
        title = lines[1].strip() if len(lines) > 1 else None
        author_name = lines[2].strip() if len(lines) > 2 else None
        author_email = lines[3].strip() if len(lines) > 3 else None
        _date = lines[4].strip() if len(lines) > 4 else None
        
        
        branch = None
        parent = None
        description_lines = []
        in_description = False
        
        for line in lines[5:]:
            cleaned = line.strip()

            if stat_re.match(line):
                break


            if cleaned.startswith("Parents:"):
                parts = cleaned.split("Parents:")
                if len(parts) > 1 and parts[1].strip():
                    parent = parts[1].strip()
            elif "refs/" in cleaned:
                branch = cleaned.split("refs/")[1].replace("heads/", "")
            elif line.startswith("Description:"):
                in_description = True
                desc_start = line.split("Description:", 1)[1].split("\n")[0]
                if desc_start.strip():
                    description_lines.append(desc_start)
            elif in_description:
                description_lines.append(line)

        description = "\n".join(description_lines).strip()
        if description:
            description = (description
                           .replace("&", "\\&")
                           .replace("_", "\\_")
                           .replace("%", "\\%")
                           .replace("#", "\\#"))
            description = description.replace("\n", " \\\\ ")
        stats = stats_match
        

        commits[hash] = {
            "hash": hash,
            "title": title.replace("&", "\\&") if title else None,
            "author_name": author_name,
            "author_email": author_email,
            "date": f"{datetime.datetime.fromisoformat(_date).date()} {datetime.datetime.fromisoformat(_date).time()}" if _date else None,
            "lines_changed": (int(stats.group("insertions")) if stats and stats.group("insertions") else 0) + (int(stats.group("deletions")) if stats and stats.group("deletions") else 0),
            "insertions": int(stats.group("insertions")) if stats and stats.group("insertions") else 0,
            "deletions": int(stats.group("deletions")) if stats and stats.group("deletions") else 0,
            "branch": branch,
            "parent_id": parent,
            "description": description
        }

        if "tag:" in chunk:
            tag_match = re.compile(r"tag:\s*([^,)]+)").search(chunk)
            tag_name = tag_match.group(1) if tag_match else None
            releases[tag_name] = {
                "hash": hash,
                "tag": tag_name,
                "title": title,
                "author_name": author_name,
                "author_email": author_email,
                "date": f"{datetime.datetime.fromisoformat(_date).date()} {datetime.datetime.fromisoformat(_date).time()}" if _date else None
            }

    return { 'commits': commits, 'releases': releases}
# add tags / releases
# title and description
# tracking branch names
# markers
# filters on the cli
# check for title tags e.g. [Fix], [Feat]... + add symbol to column of table