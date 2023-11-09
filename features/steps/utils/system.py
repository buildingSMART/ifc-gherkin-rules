import csv
import glob
import os

from .misc import do_try
from pathlib import Path


def get_abs_path(rel_path):
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


def list_renamed_entities():
    dirname = os.path.dirname(__file__)
    fn_related_attr_matrix = Path(
        dirname).parent.parent / 'resources' / 'renamed_entities.csv'
    related_attr_matrix = next(
        csv.DictReader(open(fn_related_attr_matrix)))
    return list(related_attr_matrix.items())