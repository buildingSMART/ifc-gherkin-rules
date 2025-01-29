import os
import glob
import sys
import re

import pytest
import tabulate

try:
    from ..main import run, ExecutionMode
    from .utils import collect_test_files, check_filename_structure
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import run, ExecutionMode
    from test.utils import collect_test_files, check_filename_structure

rule_code_pattern = re.compile(r"^[a-zA-Z]{3}\d{3}$")
rule_codes = list(filter(lambda arg: rule_code_pattern.match(arg), sys.argv[1:]))

    
def exclude_disabled_rules(filepath):
    tags = []
    
    with open(filepath, 'r') as file:
        for line in file:
            stripped_line = line.strip()  # Remove any leading or trailing whitespace
            if stripped_line.startswith("@"):
                tags_on_line = stripped_line.split()
                tags.extend(tags_on_line)
    return '@disabled' in tags

def rule_disabled(code: str) -> bool:
    feature_paths = glob.glob(os.path.join(os.path.dirname(__file__), "../features/**/*.feature"), recursive=True)
    return next((exclude_disabled_rules(path) for path in feature_paths if os.path.basename(path).lower().startswith(code)), False)


@pytest.mark.parametrize("filename", collect_test_files())
def test_invocation(filename):
    base = os.path.basename(filename)

    # If the hyphens or structure are incorrect, the file won't be picked up by the protocol check,
    # as the correct features can't be derived from the filename.
    check_filename_structure(base)

    gherkin_results = list(run(filename, execution_mode=ExecutionMode.TESTING))

    try:
        feature_info = gherkin_results[0]
    except IndexError:  
        print('The Gherkin tests did not run for the specified test file, and the JSON report is empty. Please review the test file for any errors.')

    rule_is_disabled = feature_info['rule_is_disabled']

    ci_cd_checks = {'protocol_errors': [], 'caught_exceptions': []}
    for i in ci_cd_checks.keys():
        ci_cd_checks[i] = next((d[i] for d in gherkin_results if i in d), None)
        
    validation_outcomes = [d for d in gherkin_results[1:] if all(key not in d for key in ci_cd_checks.keys())]

    error_outcomes = [outcome for outcome in validation_outcomes if outcome['severity'] in ['Error', 'Warning']]
    activating_outcomes = [outcome for outcome in validation_outcomes if outcome['severity'] == 'Executed']


    print()
    print(base)
    print()
    print(f"{len(activating_outcomes)} activating outcome(s)")
    print(f"{len(error_outcomes)} error(s)")


    if not rule_is_disabled:
        # Because we only run unit-testfiles on the feature they are created for,
        # it means that if there is one mention of a disabled rule it applies to the
        # testfile as well and nothing needs to be printed.
        # Errors and warnings come from exceptions raised in Python and are
        # propagated by the logger. Pass results are emitted in the run() loop
        # when inspecting the json log from behave, when there have been no
        # errors, warnings or activating outcomes. This flag is
        # based on whether a then step is executed over a prior selected set of instances or applicable
        # state originating from given steps. Therefore when results without disabled messages
        # is empty, it means that the rule has not been activated. I.e given statements
        # did not result in an actionable set of instances at the time of the first then step.
        
        #first, check if there are no protocol errors
        protocol_errors = ci_cd_checks['protocol_errors']
        if protocol_errors:
            red_text = "\033[91m"
            reset_text = "\033[0m"
            print(f'{red_text}\n\nWARNING: The following protocol errors were caught:{reset_text}')
            print(tabulate.tabulate([[error] for error in protocol_errors], headers=['Details'], tablefmt='fancy_grid'))
            assert False # table should be printed before the assertion
        
        caught_exceptions = ci_cd_checks['caught_exceptions']
        if caught_exceptions:
            red_text = "\033[91m"
            reset_text = "\033[0m"
            print(f'{red_text}\n\nWARNING: The following exceptions were caught:{reset_text}')
            
            def wrap_text(text, width):
                return '\n'.join(text[i:i+width] for i in range(0, len(text), width))

            table_data = [
                [wrap_text(exc['feature'], 40), wrap_text(exc['step'], 40), exc['error_type'], wrap_text(exc['location'], 60)]
                for exc in caught_exceptions
            ]

            
            headers = ['Feature', 'Step', 'Error Type', 'Location']
            print(tabulate.tabulate(table_data, headers=headers, tablefmt='fancy_grid'))

        if base.startswith('fail'):
            assert len(error_outcomes) > 0
        elif base.startswith('pass'):
            assert len(error_outcomes) == 0 and len(activating_outcomes) and not caught_exceptions
        elif base.startswith('na'):
            assert len(error_outcomes) == 0 and len(activating_outcomes) == 0 and not caught_exceptions

    if error_outcomes:
        tabulate_results = [
            (
                f"{outcome.get('feature')} - v{outcome.get('feature_version')}", # Feature
                outcome.get('scenario'), # Scenario 
                outcome.get('last_step'), # Last Step
                outcome.get('instance_id'), # Instance
                f"Expected : {outcome.get('expected')}, Observed : {outcome.get('observed')}", # Message
                outcome.get('outcome_code') # Code
            )
            for outcome in error_outcomes
        ]
        print(tabulate.tabulate(
            [[c or '' for c in r] for r in tabulate_results],
            headers = ["Feature", "Scenario", "Last Step", "Instance", "Message", "Code"],
            maxcolwidths=[30] * len(tabulate_results[0]),
            tablefmt="simple_grid"
        ))

if __name__ == "__main__":
    pytest.main(["-s", __file__])
