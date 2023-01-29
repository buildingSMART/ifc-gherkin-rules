import os
import glob
import sys

import pytest
import tabulate

try:
    from ..main import run
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import run

test_files = glob.glob(os.path.join(os.path.dirname(__file__), "files/**/*.ifc"), recursive=True)


@pytest.mark.parametrize("filename", test_files)
def test_invocation(filename):
    results = list(run(filename))
    base = os.path.basename(filename)
    rule_code = base.split('-')[1].strip()
    results_filtered_by_rule_code = [result for result in results if rule_code.lower() in result[0].lower()]
    print()
    print(base)
    print()
    print(f"{len(results_filtered_by_rule_code)} errors")
    if results_filtered_by_rule_code:
        print(tabulate.tabulate(
            [[c or '' for c in r] for r in results_filtered_by_rule_code],
            maxcolwidths=[30] * len(results_filtered_by_rule_code[0]),
            tablefmt="simple_grid"
        ))

    if base.startswith("fail-") and 'disabled' not in results_filtered_by_rule_code:
        assert len(results_filtered_by_rule_code) > 0
    elif base.startswith("pass-") and 'disabled' not in results_filtered_by_rule_code:
        assert len(results_filtered_by_rule_code) == 0


if __name__ == "__main__":
    pytest.main(["-s", "-x", __file__])
