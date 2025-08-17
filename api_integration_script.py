"""
This script can be used to test the development API.
Initially it was designed to speed up UAT testing.
Test files on the server need to be cleaned up manually before running the script.

Manual cleanup includes
- deleting prior ifc validations for the given functional part
- uploading the test suite for the functional part

You will then need to revise the name of the functional part in the call to `check_rule_results` below.
"""

import functools
import os
from pathlib import Path

from dotenv import load_dotenv
import httpx

URL_STEM = "https://dev.validate.buildingsmart.org/api"

@functools.lru_cache(maxsize=1)
def build_headers():
    load_dotenv()
    return {
        "Authorization": f"Token {os.environ.get('DEV_API_TOKEN')}",
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


def model_by_id(model_id: str):
    hdr = build_headers()
    resp = httpx.get(
        url=f"{URL_STEM}/models/{model_id}",
        headers=hdr,
    )
    resp.raise_for_status()
    return resp.json()


def check_rule_results(rule_code: str):
    task_types_to_check = ["INDUSTRY", "NORMATIVE_IA", "NORMATIVE_IP"]
    jdata = get_all_requests().json()
    rule_code_records = list()
    if len(jdata) == 0:
        print("[INFO] No validation results found!")
    else:
        for rec in jdata:
            filename = rec['file']
            if f"fail-{rule_code.lower()}" in filename or f"pass-{rule_code.lower()}" in filename:
                rule_code_records.append(rec)

    num_rule_code_records = len(rule_code_records)
    if num_rule_code_records == 0:
        print(f"[INFO] No validation results found for {rule_code}!")
    else:
        print(f"[INFO] Checking {len(rule_code_records)} results for {rule_code}...")
        for rec in rule_code_records:
            status = None
            task_data = tasks_by_request_id(rec['public_id'])
            for td in task_data:
                task_type = td['type']
                if task_type in task_types_to_check:
                    if rule_code in td['status_reason']:
                        if task_type == "INDUSTRY":
                            status = "WARN"
                        else:
                            status = "FAIL"

            if not status:
                status = "PASS"

            filename = Path(rec['file']).stem
            expected_status = filename[:4].upper()

            if status == expected_status:
                print(f"[INFO] '{rec['file']}' result matches expected status '{expected_status}'")
            else:
                print("*** !!! ***")
                print(f"[ERROR] '{rec['file']}' result does not match expected status '{status}'")
                print("*** !!! ***\n")


if __name__ == "__main__":
    check_rule_results(rule_code="ALS005")
    # get_all_outcomes()
    # get_all_requests()
