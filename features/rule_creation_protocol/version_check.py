import subprocess
import re
from .errors import ProtocolError

def get_changed_feature_files(target_branch):
    changed_files = subprocess.getoutput(f"git diff --name-only {target_branch}").split("\n")
    feature_files = [f for f in changed_files if f.endswith(".feature")]
    return feature_files

def check_version_bump(file):
    # Compare the file from the current branch to the target_branch
    diff_output = subprocess.getoutput(f"git diff {file}")
    versions = re.findall(r"@version(\d+)", diff_output)
    versions = [int(v) for v in versions]
    if not versions:
        raise ProtocolError(
            value = None,
            message = "When changing a feature file, the version number must be bumped"
        )
    return versions[1] > versions[0]  # Check version bump


def enforce(target_branch = 'main'):
    feature_files = get_changed_feature_files(target_branch)
    for file in feature_files:
        if not check_version_bump(file):
            raise ProtocolError(
                value = None,
                message = "When changing a feature file, the version must be bumped"
            )