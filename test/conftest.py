def pytest_addoption(parser):
    """"
    Method to allow --validate-dev to pytest : 'pytest -sv --validate-dev'
    Can be accessed with pytest 'request.config.getoption("--validate-dev")'
    """
    parser.addoption(
        "--target_branch", action="store", default='development',
        help="target branch for pull requests"
    )
    parser.addoption(
        "--pull_request", action="store", default="False",
        help="indicates if the test run is for a pull request"
    )