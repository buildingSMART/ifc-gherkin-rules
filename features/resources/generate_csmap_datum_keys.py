#!/usr/bin/env python3
"""Generate features/resources/csmap_datum_keys.csv from the CS-MAP datum dictionary.

    curl -sL -o datums.asc https://trac.osgeo.org/csmap/export/HEAD/trunk/CsMapDev/Dictionaries/datums.asc
    python3 features/resources/generate_csmap_datum_keys.py datums.asc features/resources/csmap_datum_keys.csv

Re-run when pyproj/PROJ (and thus the EPSG dataset) is bumped, and record the
svn change date of datums.asc in the header line below.
"""
import csv, re, sys, datetime
src, dst = sys.argv[1], sys.argv[2]
txt = open(src, encoding='latin-1').read()
rows = []
for block in re.split(r'\n(?=DT_NAME:)', txt):
    m = re.match(r'DT_NAME:\s*(\S+)', block)
    if not m: continue
    f = dict(re.findall(r'^\s*([A-Z_]+):\s*(.*?)\s*$', block, re.M))
    epsg = f.get('EPSG', '').split('#')[0].strip()
    rows.append((m.group(1), epsg if epsg.isdigit() and epsg != '0' else '', re.sub(r'\s+', ' ', f.get('DESC_NM', '')).strip()[:80]))
rows.sort(key=lambda r: r[0].lower())
with open(dst, 'w', newline='') as fh:
    fh.write('# CS-MAP (Autodesk Civil 3D / Map 3D) geodetic datum keys, generated from datums.asc of the OSGeo CS-MAP\n')
    fh.write('# distribution (Copyright (c) 2008 Autodesk, Inc., BSD license). Snapshot 2025-02-16, EPSG sync 11.008.\n')
    w = csv.writer(fh, lineterminator='\n'); w.writerow(['key', 'epsg_datum_code', 'description']); w.writerows(rows)
print(f'{dst}: {len(rows)} keys, {sum(1 for r in rows if r[1])} with EPSG code')
