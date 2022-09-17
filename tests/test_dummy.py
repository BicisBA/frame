import pytest


def test_dummy():
    try:
        from frame import __version__

        assert __version__ >= "0.1.0"
    except Exception as e:  # pylint: disable=broad-except
        pytest.fail(e)
