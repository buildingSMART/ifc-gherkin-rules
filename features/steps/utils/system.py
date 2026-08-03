import csv
import functools
import glob
import os

from .misc import do_try
from pathlib import Path


@functools.lru_cache(maxsize=None)
def get_abs_path(rel_path):
    # The resources/** tree does not change during a run, so the (recursive) glob
    # result is stable. Without caching this walks the filesystem on every call —
    # which is per-instance for rules that resolve attribute matrices in a Then.
    dir_name = os.path.dirname(__file__)
    parent_path = Path(dir_name).parent.parent
    csv_path = do_try(lambda: glob.glob(os.path.join(parent_path, rel_path), recursive=True)[0])
    return csv_path


def get_csv(abs_path, return_type='list', newline='', delimiter=',', quotechar='|'):
    with open(abs_path, newline=newline) as csvfile:
        if return_type == 'dict':
            reader = csv.DictReader(csvfile)
        elif return_type == 'list':
            reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        return [row for row in reader]

@functools.lru_cache(maxsize=None)
def load_attribute_matrix(table, base_folder = "resources/**/"):
    # Cached: the matrix CSVs are static per run and read-only at the call sites.
    filename = get_abs_path(f"{base_folder}{table}")
    # filename = f"{base_path}{table}"

    attr_matrix = get_csv(filename, return_type='dict')[0]
    return attr_matrix
