"""
This script can be used to test the development API.
Initially it was designed to speed up UAT testing.
Test files on the server need to be cleaned up manually before running the script.

Manual cleanup includes
- deleting prior ifc validations for the given functional part
- uploading the test suite for the functional part

You will then need to revise the name of the functional part in the call to `check_rule_results` below.
"""
import sys
from enum import Enum
import functools
import os
from pathlib import Path
from typing import List, Dict


from dotenv import load_dotenv
import httpx

class SeverityEnum(Enum):
    NA = 0
    EXECUTED = 1
    PASSED = 2
    WARNING = 3
    ERROR = 4

environment = 'DEV'
environment = 'LOCAL'

load_dotenv()
URL_STEM = os.environ.get(f"{environment}_API_ENDPOINT")
TOKEN = os.environ.get(f"{environment}_API_TOKEN")

@functools.lru_cache(maxsize=1)
def build_headers():
    return {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json"
    }


def get_all_outcomes():
    hdr = build_headers()

    # NOTE: timeout is required due to the large volume of results and pagination not implemented yet
    resp = httpx.get(
        url=URL_STEM + "validationoutcome",
        headers=hdr,
        timeout=60,
    )
    resp.raise_for_status()


def get_all_requests():
    hdr = build_headers()

    # NOTE: timeout is required due to the large volume of results and pagination not implemented yet
    resp = httpx.get(
        url=f"{URL_STEM}/validationrequest",
        headers=hdr,
        timeout=60,
    )
    resp.raise_for_status()

    return resp

def delete_request_by_id(request_id: str) -> None:
    hdr = build_headers()
    params = {"public_id": request_id}
    resp = httpx.delete(
        url=f"{URL_STEM}/validationrequest/{request_id}",
        headers=hdr,
    )
    resp.raise_for_status()

def delete_requests(requests: List[Dict]):
    for request in requests:
        delete_request_by_id(request_id=request["public_id"])

def tasks_by_request_id(request_id: str):
    hdr = build_headers()
    params = {"request_public_id": request_id}
    resp = httpx.get(
        url=f"{URL_STEM}/validationtask",
        headers=hdr,
        params=params,
        timeout=60,
    )
    match resp.status_code:
        case 200:
            return resp.json()
        case 404:
            return []
        case _:
            resp.raise_for_status()
            return None


def outcomes_by_request_id(request_id: str):
    hdr = build_headers()
    params = {"request_public_id": request_id}
    resp = httpx.get(
        url=f"{URL_STEM}/validationoutcome",
        headers=hdr,
        params=params,
        timeout=60,
    )

    resp.raise_for_status()
    return resp.json()


def model_by_id(model_id: str):
    hdr = build_headers()
    resp = httpx.get(
        url=f"{URL_STEM}/models/{model_id}",
        headers=hdr,
    )
    resp.raise_for_status()
    return resp.json()


def find_previous_validation_requests(rule_code: str) -> List[Dict]:
    """
    Finds all previous validation requests for the provided rule code and deletes them.
    """
    jdata = get_all_requests().json()
    rule_code_validation_requests = list()
    if len(jdata) == 0:
        print("[INFO] No validation results found!")
    else:
        for rec in jdata:
            filename = rec['file']
            if f"fail-{rule_code.lower()}" in filename or f"pass-{rule_code.lower()}" in filename:
                rule_code_validation_requests.append(rec)

    num_rule_code_requests = len(rule_code_validation_requests)
    if num_rule_code_requests == 0:
        print(f"[INFO] No validation results found for {rule_code}!")
        return list()
    else:
        print(f"[INFO] Found {num_rule_code_requests} validation requests for {rule_code}!")
        return rule_code_validation_requests




def check_rule_results(validation_requets: List[Dict]):

        print(f"[INFO] Checking {len(rule_code_validation_requests)} results for {rule_code}...")
        for rec in rule_code_validation_requests:
            status = None
            print(f"[INFO] Getting outcomes for '{rec['file']}'...")
            outcomes = outcomes_by_request_id(rec['public_id'])

            severity = SeverityEnum(0)
            for outcome in outcomes:
                feature = outcome['feature']
                if feature:
                    feature_code = feature.split(" ")[0]
                    if feature_code == rule_code:
                        severity = SeverityEnum(outcome['severity'])

            filename = Path(rec['file']).stem
            expected_status = filename[:4].upper()

            match expected_status:
                case "PASS":
                    if severity in [SeverityEnum.EXECUTED, SeverityEnum.PASSED]:
                        outcome_matches_expected = True
                case "FAIL":
                    if severity in [SeverityEnum.ERROR, SeverityEnum.WARNING]:
                        outcome_matches_expected = True
                case "NA":
                    if severity == SeverityEnum.EXECUTED:
                        outcome_matches_expected = True
                case _:
                    outcome_matches_expected = False

            if outcome_matches_expected:
                print(f"[INFO] '{rec['file']}' result matches expected status '{expected_status}'")
            else:
                print("*** !!! ***")
                print(f"[ERROR] '{rec['file']}' result does not match expected status '{status}'")
                print("*** !!! ***\n")


if __name__ == "__main__":
    prev_requests = find_previous_validation_requests(rule_code="ALB021")
    delete_requests(prev_requests)
    print(prev_requests)

    # check_rule_results(rule_code="ALB031")
    # get_all_outcomes()
    # get_all_requests()
