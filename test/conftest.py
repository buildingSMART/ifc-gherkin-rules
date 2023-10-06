def pytest_addoption(parser):
    """"
    Method to allow --validate-dev to pytest : 'pytest -sv --validate-dev'
    Can be accessed with pytest 'request.config.getoption("--validate-dev")'
    """
    parser.addoption(
        "--validate-dev", action="store_true", default=False,
        help="Enforce development conventions."
    )