"""

In case of validating entity attribute lookup in the behave stack tree, 
it woul dbe useful to differnetiate between a standard 'None' and a custom representation of 'None'
that behaves similarly to the built-in `None` 
but can be distinguished from it. The `VSNoneType` class follows the singleton pattern, ensuring 
that only one instance of this custom `None` type exists.

The custom `None` type is useful in scenarios where we need to differentiate between a standard 
`None` and a custom representation of `None`. This is e.g. the case with validating entity attribute lookup in the behave stack tree. 

Usage:
    from custom_none import VSNone

    print(VSNone)            # VSNone
    print(VSNone == None)    # True
    print(VSNone is None)    # False
    print(bool(VSNone))      # False
"""

class VSNoneType:
    """
    VSNoneType is a singleton class that provides a custom `None` type. This custom type 
    behaves like the built-in `None` but can be distinguished from it in comparisons and identity checks.
    """
    _instance = None

    def __new__(cls):
        """
        singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(VSNoneType, cls).__new__(cls)
        return cls._instance

    def __repr__(self):
        return 'VSNone'

    def __eq__(self, other):
        """
        Compare VSNoneType instances with other objects. Return True if the other object 
        is an instance of VSNoneType or is the built-in None.
        """
        return isinstance(other, VSNoneType) or other is None

    def __bool__(self):
        return False

VSNone = VSNoneType()

if __name__ == "__main__":
    # for experimenting in the terminal
    print(VSNone)            # VSNone
    print(VSNone == None)    # True
    print(VSNone is None)    # False
    print(bool(VSNone))      # False
