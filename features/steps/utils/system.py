import csv
import glob
import os

from .misc import do_try
from pathlib import Path


def get_abs_path(rel_path):
    dir_name = os.path.dirname(__file__)
    parent_path = Path(dir_name).parent.parent
    results = glob.glob(os.path.join(parent_path, rel_path), recursive=True)
    if '**' in rel_path:
        # assume recursive search to single resource
        return do_try(lambda: results[0])
    elif '*' in rel_path:
        # assume search to multiple files in pattern
        return results
    else:
        return do_try(lambda: results[0])


def get_csv(abs_path, return_type='list', newline='', delimiter=',', quotechar='|'):
    with open(abs_path, newline=newline) as csvfile:
        if return_type == 'dict':
            reader = csv.DictReader(csvfile)
        elif return_type == 'list':
            reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        return [row for row in reader]
