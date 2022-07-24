import glob

import pytest

from ..main import run

test_files = glob.glob("files/*.ifc")
@pytest.mark.parametrize("filename", test_files)
def test_invocation(filename):
    run(filename)

if __name__ == "__main__":
    pytest.main(["-x", __file__])
