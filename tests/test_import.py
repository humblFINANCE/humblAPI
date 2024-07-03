"""Test humblapi."""

import humblapi


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(humblapi.__name__, str)
