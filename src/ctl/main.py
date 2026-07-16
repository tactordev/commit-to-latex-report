import os, shutil, re, os, subprocess, argparse, tempfile
from .latex import Document, Table


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
    out = subprocess.check_output(["git", "log", "--stat",
        "--date=iso-strict",
        "--pretty=format:@@COMMIT@@%n%H%n%an%n%ae%n%ad",], cwd=path)


    with open("out.tex", "w") as f:
        f.write(report(out))

    subprocess.run([
        "xelatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "out.tex",
    ], check=True)

    if not os.path.exists("out.pdf"):
        return print("PDF file not generated.")

    print("Cleaning up temporary files...")

    if temp_dir is not None:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("PDF file generated: file:///" + os.path.abspath("out.pdf"), "(CTRL + Click to open).")
    return


def parseLog(raw: bytes):
    global path
    raw = raw.decode("utf-8")
    
    print("Getting origin URL...")
    origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=path).decode("utf-8").strip()


    print("Parsing git log output...")

    commits = []

    for chunk in re.compile(r"^@@COMMIT@@$", re.MULTILINE).split(raw):
        chunk = chunk.strip("\n")
        if not chunk.strip():
            continue

        lines = chunk.split("\n")
        hash = lines[0].strip() if len(lines) > 0 else None
        author_name = lines[1].strip() if len(lines) > 1 else None
        author_email = lines[2].strip() if len(lines) > 2 else None
        date = lines[3].strip() if len(lines) > 3 else None

        stats = re.compile(
            r"^\s*\d+ files? changed"
            r"(?:, (?P<insertions>\d+) insertions?\(\+\))?"
            r"(?:, (?P<deletions>\d+) deletions?\(-\))?\s*$",
            re.MULTILINE
        ).search(chunk)
        

        commits.append({
            "origin": origin if origin is not None else "main/",
            "hash": hash,
            "author_name": author_name,
            "author_email": author_email,
            "date": date,
            "insertions": int(stats.group("insertions")) if stats and stats.group("insertions") else 0,
            "deletions": int(stats.group("deletions")) if stats and stats.group("deletions") else 0
        })

    return commits


def report(out):
    doc = Document()
    commits = parseLog(out)

    texFormat = ""
    for commit in commits:
        texFormat += f"\\href[[{commit["origin"][:-4] if ".git" in commit["origin"] else commit["origin"]}/commits/{commit["hash"]}]][[\\textbf[[{commit["hash"]}]]]] & {commit["author_name"]} & {commit["date"]} & \\color[green]{commit["insertions"]} & \\color[red]{commit["deletions"]} \\\\ \\hline\n"
    doc.add("table", texFormat)
    return doc.render()


# add tags / releases
# title and description
# tracking branch names
# markers
# filters on the cli
# check for title tags e.g. [Fix], [Feat]... + add symbol to column of table