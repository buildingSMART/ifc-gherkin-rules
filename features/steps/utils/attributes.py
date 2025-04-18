import re 

def condition_met(value, condition, expected):
    """
    Generic function to check if a given value meets the specified condition.

    Used in statements such as
    - "Its value does not start with 'Pset_'"
    - "Its value starts with '0' or '1' or '2' or '3'"
    - "Its name attribute starts with" 
    """
    if condition == "starts":
        return value.startswith(expected)
    elif condition in ("does not start", "must not start"):
        return not value.startswith(expected)
    elif condition == "conforms":
        return re.match(expected, value) is not None
    elif condition in ("does not conform", "must not conform"):
        return re.match(expected, value) is None
    return False  # Default, should not be reached but in that case Gherkin CI/CD will catch it 
