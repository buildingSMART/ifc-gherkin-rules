import os
import glob
import sys

import pytest

try:
    from ..main import run
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import run    

test_files = glob.glob(os.path.join(os.path.dirname(__file__), "files/*.ifc"))
@pytest.mark.parametrize("filename", test_files)
def test_invocation(filename):
    results = list(run(filename))
    base = os.path.basename(filename)
    print(base, len(results))
    if base.startswith("fail-"):
        assert len(results) > 0
    elif base.startswith("pass-"):
        assert len(results) == 0

if __name__ == "__main__":
    pytest.main(["-s", "-x", __file__])
