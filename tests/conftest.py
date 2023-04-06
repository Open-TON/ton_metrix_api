"""Code shared across tests."""
# flake8: noqa
from asyncio import get_running_loop
from asyncio import new_event_loop

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Default for all async tests."""
    try:
        loop = get_running_loop()
    except RuntimeError:
        loop = new_event_loop()
    yield loop
    loop.close()
