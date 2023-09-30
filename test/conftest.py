def pytest_addoption(parser):
    parser.addoption(
        "--validate-dev", action="store_true", default=False,
        help="Enforce development conventions."
    )