import pytest

from mrhscrypto import MRHSCrypto


@pytest.fixture(scope="session")
def keypair():
    return MRHSCrypto.generate_keypair(d=1, security=128)