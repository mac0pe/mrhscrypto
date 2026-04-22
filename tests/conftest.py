import pytest

from mrhscrypto import MRHSCrypto


@pytest.fixture(scope="session")
def keypair():
    return MRHSCrypto.generate_keypair(d=1, security=128)


@pytest.fixture
def message_128():
    return b"1234567890abcdef"  # 16 bytes = 128 bits