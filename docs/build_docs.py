import json
import linecache
import os
import shutil
import subprocess, re
from collections import defaultdict
import sys

from git import version_events_for_file, path_exists_in_ref

from git import git  # if you export it, or roll a tiny helper

current_branch = git("branch", "--show-current")
print(f"Building docs for branch: {current_branch!r}") # for ci_cd logging

from paths import (
    SCRIPT_DIR,
    REPO_ROOT,
    DOCS_DIR,
    FEATURES_DIR,
    STEPS_DIR,
    BUILD_DIR,
    CONF_SRC,
    FUNCTIONAL_PARTS_JSON,
)

USAGE_CMD = [
    sys.executable,
    "-m",
    "behave",
    "--format=steps.usage",
    "--dry-run",
    "--no-summary",
    "-q",
]
CATALOG_CMD = [
    sys.executable,
    "-m",
    "behave",
    "--format=steps.catalog",
    "--dry-run",
    "--no-summary",
    "-q",
]

def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True, cwd=REPO_ROOT)
    print(proc.stderr)
    return proc.stdout

def parse_usage(output):
    """
    Parse the output of --format=steps.usage into a list of dicts:
      {
        'pattern':  decorator string,
        'def_file': defining .py file,
        'def_line': line number,
        'usages': [ (kind, text, feature_loc), ... ]
      }
    """
    entries = []
    lines = output.splitlines()
    i = 0

    step_re    = re.compile(r"^@step\('(.+)'\)\s*#\s*(.+):(\d+)")
    usage_re   = re.compile(r"^\s*(Given|When|Then)\s+(.+?)\s*#\s*(.+:\d+)")
    while i < len(lines):
        m = step_re.match(lines[i])
        if m:
            pattern, def_file, def_line = m.groups()
            usages = []
            i += 1
            # collect following indented usage lines
            while i < len(lines) and lines[i].strip():
                mu = usage_re.match(lines[i])
                if mu:
                    kind, text, loc = mu.groups()
                    usages.append((kind, text, loc))
                i += 1
            entries.append({
                'pattern':  pattern,
                'def_file': def_file,
                'def_line': def_line,
                'usages':   usages,
            })
        else:
            i += 1

    return entries

def parse_catalog_docs(output):
    """
    Parse documentation from --format=steps.catalog.
    Returns a dict mapping pattern -> doc string (possibly multi-line).
    """
    docs = {}
    lines = output.splitlines()
    i = 0
    # matches "Given <pattern>"
    pat_re = re.compile(r"^(Given|When|Then)\s+(.+)$")
    while i < len(lines):
        m = pat_re.match(lines[i])
        if m and m.group(1) == "Given":
            # first line of a block
            pattern = m.group(2).strip()
            # skip the next two lines (When, Then)
            i += 3
            # collect indented doc lines
            doc_lines = []
            while i < len(lines) and lines[i].startswith("    ") and not pat_re.match(lines[i]):
                doc_lines.append(lines[i].strip())
                i += 1
            if doc_lines:
                docs[pattern] = "\n".join(doc_lines)
        else:
            i += 1
    return docs


def load_functional_parts():
    """
    Load functional part metadata from fixtures/functional_parts.json
    Ideally, the scorecards would load from there

    Expected JSON shape (per entry):

      {
        "pk": "ALB",
        "fields": {
          "name": "Alignment",
          "description": "...",
          "created": "...",
          "parent": "POS",
          "span": 2,
          "display_order": 0
        }
      }
    'Parent' and 'created' are ignored for now 
    to do: also add an 'last updated' based on the last git commit and update the json accordingly?
    """
    with open(FUNCTIONAL_PARTS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    parts = {}
    for obj in data:
        code = obj["pk"]
        fields = obj.get("fields", {})
        parts[code] = fields
    return parts


def main():
    usage_output  = run(USAGE_CMD)
    catalog_output = run(CATALOG_CMD)

    steps = parse_usage(usage_output)
    docs_map = parse_catalog_docs(catalog_output)
    functional_parts = load_functional_parts()

    by_file = defaultdict(list)
    for s in steps:
        by_file[s['def_file']].append(s)

    by_usage = {}
    for s in steps:
        for us in s['usages']:
            by_usage[us[2]] = re.sub(r'[^\w]', '', f'{"/".join(s["def_file"].split("/")[2:])}_{s["pattern"]}')

    shutil.rmtree(DOCS_DIR, ignore_errors=True)

    os.makedirs(STEPS_DIR, exist_ok=True)
    os.makedirs(FEATURES_DIR, exist_ok=True)
    shutil.copyfile(CONF_SRC, os.path.join(DOCS_DIR, "conf.py"))

    all_feature_files = sorted(set(a[2].rsplit(':', 1)[0] for s in steps for a in s['usages']))


    # ------------------------------------------------------------------
    # Per-feature pages
    # ------------------------------------------------------------------
    
    for feat in all_feature_files:
        base = os.path.basename(feat).rsplit('.', 1)[0]
        
        feature_file_path = os.path.join(REPO_ROOT, feat)
        
        feature_file_text = open(feature_file_path, encoding="utf-8").read()
        
        m_ver = re.search(r"@version\s*(\d+)", feature_file_text)
        version = int(m_ver.group(1)) if m_ver else None
        
        disabled = "@disabled" in feature_file_text
        with open(os.path.join(FEATURES_DIR, f"{base}.rst"), "w", encoding="utf-8") as feature_file:
            WARN = '\\( \u26A0 '
            END_WARN = '\\) \\(disabled\\)'
            
            rule_code = base[:6]
            rule_title = base[7:].replace("-", " ").replace("_", " ")
            version_suffix = f" - v{version}" if version is not None else ""
            feature_file.write(
                f"{WARN if disabled else ''}"
                f"``{rule_code}`` {rule_title}{version_suffix}"
                f"{END_WARN if disabled else ''}\n"
            )
            feature_file.write(f"{'='*200}\n\n")
            feature_file.write(f".. parsed-literal::\n\n")
            for ln, st in enumerate(linecache.getlines(feature_file_path), start=1):
                ref = f"{feat}:{ln}"
                esc = (
                    lambda s: s.replace("@", "\\@")
                    .replace("_", "\\_")
                    .replace("<", "\\<")
                    .replace(">", "\\>")
                )
                text = esc(st.rstrip())
                if dd := by_usage.get(ref):
                    n = len(text)
                    text = text.lstrip()
                    ws = " " * (n - len(text))
                    text = f"{ws}:doc:`{text} </steps/{dd}>`"
                feature_file.write(f"   {ln:03d} | {text}")
                feature_file.write("\n")

            # -------------------------
            # Version history section
            # -------------------------
            events = version_events_for_file(feat)

            if events:
                feature_file.write("\n.. rubric:: Version history\n\n")
                feature_file.write(".. list-table::\n")
                feature_file.write("   :header-rows: 1\n\n")
                feature_file.write("   * - Version\n")
                feature_file.write("     - Tag\n")
                feature_file.write("     - Date\n")
                feature_file.write("     - Commit\n")
                feature_file.write("     - Rule link\n")
                
                for ev in events:
                    from conf import GITHUB_BASE
                    ver = f"v{ev['version']}"
                    raw_tag = ev["tag"]
                    date = ev["date"]
                    sha = ev["commit"]

                    if raw_tag:
                        tag_cell = f":tag:`{raw_tag}`"

                        branch_version = raw_tag.lstrip("v")

                        new_layout_path = feat
                        old_layout_path = os.path.join("features", os.path.basename(feat))

                        if path_exists_in_ref(raw_tag, new_layout_path):
                            feat_git_url = new_layout_path
                        elif path_exists_in_ref(raw_tag, old_layout_path):
                            feat_git_url = old_layout_path
                        else:
                            feat_git_url = None

                        if feat_git_url:
                            rule_url = f"{GITHUB_BASE}/blob/release/{branch_version}/{feat_git_url}"
                            rule_link_cell = f"`view <{rule_url}>`_"
                        else:
                            rule_link_cell = "n/a"
                    else:
                        tag_cell = "n/a"
                        rule_link_cell = "n/a"

                    feature_file.write(f"   * - {ver}\n")
                    feature_file.write(f"     - {tag_cell}\n")
                    feature_file.write(f"     - {date}\n")
                    feature_file.write(f"     - :commit:`{sha}`\n")
                    feature_file.write(f"     - {rule_link_cell}\n")

    # ------------------------------------------------------------------
    # Group feature bases by functional-part code (first 3 chars, e.g. ALB)
    # and create one page per functional part.
    # ------------------------------------------------------------------
    grouped = defaultdict(list)
    for feat in all_feature_files:
        base = os.path.basename(feat).rsplit(".", 1)[0]
        fp_code = base[:3]
        grouped[fp_code].append(base)

    def fp_sort_key(fp_code):
        info = functional_parts.get(fp_code, {})
        return (info.get("display_order", 9999), fp_code)

    # One .rst file per functional part: Alignment (ALB), etc.
    for fp_code in sorted(grouped.keys(), key=fp_sort_key):
        info = functional_parts.get(fp_code, {})
        name = info.get("name", fp_code)
        desc = info.get("description", "")

        title = f"{name} (``{fp_code}``)"
        
        with open(os.path.join(FEATURES_DIR, f"{fp_code}.rst"), "w", encoding="utf-8") as fp_file:
            fp_file.write(f"{title}\n")
            fp_file.write(f"{'=' * len(title)}\n\n")

            if desc:
                fp_file.write(desc + "\n\n")

            fp_file.write(".. toctree::\n\n")
            fp_file.write("   :titlesonly:\n\n")
            for base in sorted(set(grouped[fp_code])):
                fp_file.write(f"   {base}\n")
            fp_file.write("\n")

    # ------------------------------------------------------------------
    # features/index.rst: toctree of functional-part pages
    # ------------------------------------------------------------------
    with open(os.path.join(FEATURES_DIR,"index.rst"), "w", encoding="utf-8") as feature_index:
        feature_index.write("Validation Service Rule Definitions\n")
        feature_index.write("===================================\n\n")
        feature_index.write(".. toctree::\n")
        feature_index.write("   :titlesonly:\n\n")
        for fp_code in sorted(grouped.keys(), key=fp_sort_key):
            feature_index.write(f"   {fp_code}\n")

    # ------------------------------------------------------------------
    # steps/index.rst
    # ------------------------------------------------------------------
    with open(os.path.join(STEPS_DIR,"index.rst"), "w") as step_index:
        step_index.write("Behave Step Implementations\n")
        step_index.write("===========================\n\n")
        step_index.write(".. toctree::\n\n")
        for s in dict(sorted({s['pattern']: s for s in steps}.items())).values():
            fn = re.sub(r'[^\w]', '', f'{"/".join(s["def_file"].split("/")[2:])}_{s["pattern"]}')
            step_index.write(f"  {fn}\n")
        
            with open(os.path.join(STEPS_DIR,f"{fn}.rst"), "w") as step_doc:
                pat = s['pattern'].replace('{', '``').replace('}', '``')
                pat = pat.replace(".", "\\ .\\ ")
                pat = pat.replace("^", "\\ ^\\ ")
                step_doc.write(f"{pat}\n")
                step_doc.write(f"{'='*len(pat)}\n\n")
                if doc := docs_map.get(s['pattern'], '').strip():
                    step_doc.write(f".. container:: prewrap\n\n")
                    pref = '   | '
                    for line in doc.splitlines():
                        step_doc.write(f"{pref}{line}\n")
                        if line.lower().strip() == 'args:':
                            pref = '   | - '
                    step_doc.write("\n")
                
                step_doc.write("Usages:\n")
                step_doc.write("~~~~~~~\n\n")

                for kind, text, loc in s['usages']:
                    fn, ln = '/'.join(loc.split('/')[2:]).split(':')
                    step_doc.write(f" - **{kind}** *{text}*\n\n   :doc:`/features/{os.path.basename(fn).rsplit('.', 1)[0]}`:{ln}\n\n")
                step_doc.write("\n")

    # ------------------------------------------------------------------
    # main index.rst
    # ------------------------------------------------------------------
    with open(os.path.join(DOCS_DIR,"index.rst"), "w") as main_index:
        main_index.write("""
IFC Gherkin Rules Documentation
===============================

This documentation contains the feature definitions and step implementations
used for IFC-based rule validation in Gherkin format as used by the bSI
validation service.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   features/index
   steps/index
                         
.. list-table:: Version history
   :header-rows: 1

""")

        from git import process_version_info
        for i, f in enumerate(all_feature_files):
            tags, versions = zip(*process_version_info(f))
            if i == 0:
                print(f'   * - rule', file=main_index)
                for t in tags:
                    print(f'     - {t}', file=main_index)
            print(f'   * - ``{os.path.basename(f)[0:6]}``', file=main_index)
            for v in versions:
                print(f'     - {"v" if v else ""}{v if v else "n/a"}', file=main_index)
    
    if sb := shutil.which("sphinx-build"):
        subprocess.run([sb, DOCS_DIR,  BUILD_DIR])


if __name__ == "__main__":
    main()
