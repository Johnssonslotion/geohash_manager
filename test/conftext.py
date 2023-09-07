from geohash_manager import GeohashManager
import pytest


@pytest.fixture(scope="session")
def manager():
    return GeohashManager()
