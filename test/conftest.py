import random
import string
from typing import Dict
from geohash_manager import GeohashManager
import pytest


@pytest.fixture(scope="session")
def manager():
    return GeohashManager()


@pytest.fixture(scope="module")
def util_random_string():
    return random_lower_string()


@pytest.fixture(scope="module")
def util_random_string():
    return random_lower_string()


@pytest.fixture(scope="module")
def util_random_email():
    return random_email()


@pytest.fixture(scope="module")
def util_latlng():
    return random_latlng()


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_latlng() -> Dict[str, float]:
    return {
        "lat": random.uniform(37.4, 37.7),
        "lng": random.uniform(126.8, 127.2),
    }
