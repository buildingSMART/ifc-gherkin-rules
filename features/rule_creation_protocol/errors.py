class ProtocolError(AssertionError):
    """Custom exception for errors related to rule protocol.

    This exception is raised when there's a violation or error related to the rule protocol.
    """

    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)
