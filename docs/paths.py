import os

# directory where this file lives (docs/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

REPO_ROOT = os.path.dirname(SCRIPT_DIR)

# documentation directories
DOCS_DIR = os.path.join(SCRIPT_DIR, "_docs")
FEATURES_DIR = os.path.join(DOCS_DIR, "features")
STEPS_DIR = os.path.join(DOCS_DIR, "steps")
BUILD_DIR = os.path.join(SCRIPT_DIR, "_build")

# files
CONF_SRC = os.path.join(SCRIPT_DIR, "_conf.py")
FUNCTIONAL_PARTS_JSON = os.path.join(SCRIPT_DIR, "fixtures", "functional_parts.json")
