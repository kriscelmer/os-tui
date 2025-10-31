import os_tui


def test_package_has_version_attribute() -> None:
    assert hasattr(os_tui, "__version__"), "Package should define __version__ for introspection"
