"""Pytest configuration for Kelly & Pruitt (2013) replication test suite."""


def pytest_configure(config):
    # Suppress DeprecationWarning from pandas_datareader using distutils.version.LooseVersion.
    # This is a known issue in the pandas_datareader package and not something we can fix.
    config.addinivalue_line(
        "filterwarnings",
        "ignore:distutils Version classes are deprecated:DeprecationWarning",
    )
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )
