import subprocess
import os
import time
import re
from .latex import Document, Table
import argparse


def main() -> None:
    global path

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the git repository")
    args = parser.parse_args()
    path = args.path

    print("Running git log command...")
    out = subprocess.check_output(["git", "log", "--stat", "--after=\"2026-07-01\""], cwd=path)

    lines = out.splitlines()


    with open("out.txt", "w") as f:
        f.write(report(out))
        print("Report exported to out.txt.")
    return


def parseLog(out):
    global path
    rows = ""
    
    print("Getting origin URL...")
    origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=path).decode("utf-8").strip()


    print("Parsing git log output...")
    for log in re.split(r"\n\ncommit ", out.decode("utf-8")):
        if log.strip() == "":
            continue
            
        hash = log.splitlines()[0]
        
        fullAuthor = log.splitlines()[1].split(": ")[1]
        authorName = fullAuthor.split("<")[0].strip()
        authorEmail = fullAuthor.split("<")[1].split(">")[0].strip()
        
        authorLocalisedDate = log.splitlines()[2].split(": ")[1]
        offsetHrs = int(authorLocalisedDate.split(" +")[1][:3]) if "+" in authorLocalisedDate else -int(authorLocalisedDate.split(" -")[1][:2])
        offsetMins = int(authorLocalisedDate.split(" +")[1][3:]) if "+" in authorLocalisedDate else -int(authorLocalisedDate.split(" -")[1][3:])

        currentHrs = authorLocalisedDate.split(":")[0].split(" ")[-1]
        currentMins = authorLocalisedDate.split(":")[1].split(":")[0]


        updHrs = int(currentHrs) - offsetHrs
        updMins = int(currentMins) - offsetMins

        monthToNum = { "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                        "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12" }
        date = f"{authorLocalisedDate.split(":")[2].split(" ")[1].split(" ")[0]}-{monthToNum[re.split(r"[\s]", authorLocalisedDate)[3]]}-{re.split(r"[\s]", authorLocalisedDate)[4]}"

        insertions = log.split(" insertions")[0].split("changed, ")[1] if "insertions" in log else "0"
        
        if "deletions" in log:
            if "insertions" in log:
                deletions = log.split(" deletions(-)")[0].split("insertions(+), ")[1]
            else:
                deletions = log.split("changed, ")[1].split(" deletions(-)")[0]
        else:
            deletions = "0"
        

        rows += f"\\href[[{origin[:-4]}/commit/{hash.split("commit ")[1] if "commit" in hash else hash}]][[\\textbf[[{hash.split("commit ")[1][:5] if "commit" in hash else hash[:5]}]]]] & {authorName} & {date} & \\color[green]{insertions} & \\color[red]{deletions} \\\\ \\hline\n"
    return rows

def report(out):
    doc = Document()
    doc.add("table", parseLog(out))
    return doc.render()

