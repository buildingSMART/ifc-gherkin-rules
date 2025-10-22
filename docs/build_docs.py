import linecache
import os
import shutil
import subprocess, re
from collections import defaultdict

USAGE_CMD = [
    "behave",
    "--format=steps.usage",
    "--dry-run",
    "--no-summary",
    "-q",
]
CATALOG_CMD = [
    "behave",
    "--format=steps.catalog",
    "--dry-run",
    "--no-summary",
    "-q",
]

def run(cmd, **kwargs):
    return subprocess.run(cmd, text=True, capture_output=True, **kwargs).stdout

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



def main():
    usage_output   = run(USAGE_CMD, cwd='..')
    catalog_output = run(CATALOG_CMD, cwd='..')

    steps = parse_usage(usage_output)
    docs_map = parse_catalog_docs(catalog_output)

    by_file = defaultdict(list)
    for s in steps:
        by_file[s['def_file']].append(s)

    by_usage = {}
    for s in steps:
        for us in s['usages']:
            by_usage[us[2]] = re.sub(r'[^\w]', '', f'{"/".join(s["def_file"].split("/")[2:])}_{s["pattern"]}')

    shutil.rmtree('_docs', ignore_errors=True)
    
    os.makedirs("_docs/steps", exist_ok=True)
    os.makedirs("_docs/features", exist_ok=True)
    shutil.copyfile('_conf.py', '_docs/conf.py')

    all_feature_files = sorted(set(a[2].rsplit(':', 1)[0] for s in steps for a in s['usages']))

    with open("_docs/features/index.rst", "w") as feature_index:
        feature_index.write("Validation Service Rule Definitions\n")
        feature_index.write("===================================\n\n")
        feature_index.write(".. toctree::\n\n")
        for feat in all_feature_files:
            base = os.path.basename(feat).rsplit('.', 1)[0]
            feature_index.write(f"  {base}\n")
            with open(f"_docs/features/{base}.rst", "w") as feature_file:
                feature_file.write(f"``{base[:6]}`` {base[7:].replace('-', ' ').replace('_', ' ')}\n")
                feature_file.write(f"{'='*200}\n\n")
                feature_file.write(f".. parsed-literal::\n\n")
                for ln, st in enumerate(linecache.getlines('../'+feat), start=1):
                    ref = f'{feat}:{ln}'
                    esc = lambda s: s.replace('@', '\\@').replace("_", "\\_").replace("<", "\\<").replace(">", "\\>")
                    text = esc(st.rstrip())
                    if dd := by_usage.get(ref):
                        n = len(text)
                        text = text.lstrip()
                        ws = ' ' * (n - len(text))
                        text = f"{ws}:doc:`{text} </steps/{dd}>`"
                    feature_file.write(f"   {ln:03d} | {text}")
                    feature_file.write("\n")

    with open("_docs/steps/index.rst", "w") as step_index:
        step_index.write("Behave Step Implementations\n")
        step_index.write("===========================\n\n")
        step_index.write(".. toctree::\n\n")
        for s in dict(sorted({s['pattern']: s for s in steps}.items())).values():
            fn = re.sub(r'[^\w]', '', f'{"/".join(s["def_file"].split("/")[2:])}_{s["pattern"]}')
            step_index.write(f"  {fn}\n")
        
            with open(f"_docs/steps/{fn}.rst", "w") as step_doc:
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

    with open("_docs/index.rst", "w") as main_index:
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
        subprocess.run([sb, "_docs", "_build"])

if __name__ == "__main__":
    main()
