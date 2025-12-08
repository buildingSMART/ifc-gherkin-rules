import os
import subprocess as sp
import re
from pathlib import Path
import sys
from natsort import natsorted

from paths import REPO_ROOT

def git(*args, cwd=REPO_ROOT):
    out = sp.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    return out.stdout.strip()

def introduced_commit(path, repo):
    return (git("log", "--follow", "--diff-filter=A", "--format=%H", "-1", "--", path, cwd=repo) or '').strip()


def tags_for_commit(commit, repo):
    return natsorted(git("tag", "--contains", commit, cwd=repo).splitlines())


def all_tags(repo):
    return natsorted(git("tag", "-l", cwd=repo).splitlines())

def version_bumps_from_log(file_path, repo):
    # scan through log:
    #  - track renames (--follow) across single file
    #  - include patch content (-p)
    #  - minimal context (-U0)
    log = git("log", "--follow", "-M", "-p", "-U0", "--no-color", "--", file_path, cwd=repo)

    sha = None
    version_no_before_after = [None, None]
    current_file = None

    def flush_commit():
        if all(isinstance(v, int) for v in version_no_before_after):
            fr, to = version_no_before_after
            version_no_before_after[:] = None, None
            return {
                "commit": sha,
                "file": current_file,
                "from": fr,
                "to": to,
            }

    for line in log.splitlines():
        if line.startswith("commit ") and len(line.strip()) == 47:
            if sha:
                yield from filter(None, [flush_commit()])
            sha = line.split()[1]
            current_file = None
            continue

        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue

        if not current_file or not line or line[0] not in "+-":
            continue

        if m := re.search(r'@version\s*(\d+)', line):
            bucket = 0 if line[0] == "-" else 1
            version_no_before_after[bucket] = int(m.group(1))

    yield from filter(None, [flush_commit()])


def version_events_for_file(path, repo=REPO_ROOT):
    """
    Version changes for a rule.

    Each event is a dict:
      {
        "version": int,
        "commit": "sha1...",
        "tag": "v0.7.8",
        "date": "YYYY-MM-DD",
      }
    """
    events = []
    
    intro = introduced_commit(path, REPO_ROOT)
    try:
        tag = tags_for_commit(intro, repo)[0]
    except IndexError:
        tag = None
    events.append(
        {
            "version": 1, # introduction
            "commit": intro,
            "tag": tag,
            "date": git("show", "-s", "--format=%cd", "--date=short", intro, cwd=repo).strip() 
        }
    )
    
    for bump in reversed(list(version_bumps_from_log(path, repo))):
        commit = bump["commit"]
        to_ver = bump["to"]

        try:
            tag = tags_for_commit(commit, repo)[0]
        except IndexError:
            tag = None

        events.append(
            {
                "version": to_ver,
                "commit": commit,
                "tag": tag,
                "date": git("show", "-s", "--format=%cd", "--date=short", commit, cwd=repo).strip(),
            }
        )
    return events

def path_exists_in_ref(ref, path, repo=REPO_ROOT):
    out = git("ls-tree", ref, "--", path, cwd=repo)
    return bool(out.strip())

def process_version_info(path):
   
    tag_ids = dict(map(reversed, enumerate(all_tags(REPO_ROOT))))
    version_progression = [0] * len(tag_ids)

    intro = introduced_commit(path, REPO_ROOT)
    try:
        tag = tags_for_commit(intro, REPO_ROOT)[0]
    except IndexError as e:
        tag = None
    print("Introduced in commit:", intro, tag or 'no tag')

    if tag:
        # @todo are we sure the introduction is always v1?
        to_update = version_progression[tag_ids[tag]:]
        version_progression[tag_ids[tag]:] = [1] * len(to_update)

    print("\nVersion bumps:")        
    for b in reversed(list(version_bumps_from_log(path, REPO_ROOT))):
        try:
            tag = tags_for_commit(b['commit'], REPO_ROOT)[0]
        except IndexError as e:
            tag = None
        print(b, tag or 'no tag')
        if tag:
            # always overwrite, retain newest
            to_update = version_progression[tag_ids[tag]:]
            version_progression[tag_ids[tag]:] = [b['to']] * len(to_update)

    for t, v in zip(all_tags(REPO_ROOT), version_progression):
        print(t, f"v{v}" if v else "-")
        yield t, v or None
