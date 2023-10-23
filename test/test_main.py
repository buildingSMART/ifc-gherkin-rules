import os
import glob
import sys
import re

import pytest
import tabulate

try:
    from ..main import run
    from .utils import collect_test_files
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import run
    from test.utils import collect_test_files

    
@pytest.mark.parametrize("filename", collect_test_files())
def test_invocation(filename):
    gherkin_results = list(run(filename))
    base = os.path.basename(filename)

    # if base.startswith("pass-"):
    results = [result for result in gherkin_results if result[4] != 'Rule disabled']
    results = [result for result in results if 'Rule passed' not in result[4]]
    print()
    print(base)
    print()
    print(f"{len(results)} errors")

    if gherkin_results:
        print(tabulate.tabulate(
            [[c or '' for c in r] for r in gherkin_results],
            maxcolwidths=[30] * len(gherkin_results[0]),
            tablefmt="simple_grid"
        ))

    if base.startswith("fail-") and not any(description == 'Rule disabled' for description in [result[4] for result in gherkin_results]):
        assert len(results) > 0
    elif base.startswith("pass-"):
        assert len(results) == 0

if __name__ == "__main__":
    pytest.main(["-s", __file__])
