class Registry:
    """Registry class to store and check for duplicate feature values.

    Stores names, rule codes, and rule titles, enabling checking for duplicates in these values.
    """
    names = set()
    rule_code = set()
    rule_title = set()