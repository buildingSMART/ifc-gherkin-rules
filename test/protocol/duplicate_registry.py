from .errors import ProtocolError

class Registry:
    _rule_title_to_code = {}
    _rule_code_to_title = {}

    @classmethod
    def register_combination(cls, rule_code, rule_title):
        existing_code = cls._rule_title_to_code.get(rule_title)
        existing_title = cls._rule_code_to_title.get(rule_code)

        if existing_code and existing_code.lower() != rule_code.lower():
            raise ProtocolError(
                value=rule_title,
                message=f"Error due to duplicated names. The title '{rule_title}' has previously been linked with the code '{existing_code}'. It cannot be paired with '{rule_code}'."
            )

        if existing_title and existing_title.lower() != rule_title.lower():
            raise ProtocolError(
                value=rule_code,
                message=f"Error due to duplicated names. The code '{rule_code}' is already associated with the title '{existing_title}'. It cannot be paired '{rule_title}'."
            )

        # Register the combination if no error was raised
        cls._rule_title_to_code[rule_title] = rule_code
        cls._rule_code_to_title[rule_code] = rule_title
