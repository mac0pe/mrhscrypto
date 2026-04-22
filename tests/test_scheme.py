import numpy as np
import pytest

from mrhscrypto import MRHSCrypto
from mrhscrypto.exceptions import (
    ParameterError,
    KeyValidationError,
    MessageValidationError,
    CiphertextValidationError,
)


def test_generate_keypair_rejects_invalid_d():
    with pytest.raises(ParameterError):
        MRHSCrypto.generate_keypair(d=2, security=128)


def test_generate_keypair_rejects_invalid_security():
    with pytest.raises(ParameterError):
        MRHSCrypto.generate_keypair(d=1, security=64)


def test_scheme_can_be_created_from_public_key(keypair):
    scheme = MRHSCrypto.new(keypair.public_key)

    assert scheme.key == keypair.public_key


def test_scheme_can_be_created_from_private_key(keypair):
    scheme = MRHSCrypto.new(keypair.private_key)

    assert scheme.key == keypair.private_key


def test_encrypt_with_public_key_returns_ciphertext(keypair):
    scheme = MRHSCrypto.new(keypair.public_key)
    params = keypair.public_key.parameters

    message = np.random.randint(
        0,
        2,
        size=params.security,
        dtype=np.uint8,
    )

    ciphertext = scheme.encrypt(message)

    assert ciphertext.shape == (2 * params.m,)
    assert set(np.unique(ciphertext)).issubset({0, 1})


def test_encrypt_with_private_key_also_works(keypair):
    scheme = MRHSCrypto.new(keypair.private_key)
    params = keypair.private_key.parameters

    message = np.random.randint(
        0,
        2,
        size=params.security,
        dtype=np.uint8,
    )

    ciphertext = scheme.encrypt(message)

    assert ciphertext.shape == (2 * params.m,)
    assert set(np.unique(ciphertext)).issubset({0, 1})


def test_encrypt_rejects_wrong_message_length(keypair):
    scheme = MRHSCrypto.new(keypair.public_key)
    params = keypair.public_key.parameters

    message = np.zeros(params.security - 1, dtype=np.uint8)

    with pytest.raises(MessageValidationError):
        scheme.encrypt(message)


def test_public_key_cannot_decrypt(keypair):
    scheme = MRHSCrypto.new(keypair.public_key)
    params = keypair.public_key.parameters

    ciphertext = np.zeros(2 * params.m, dtype=np.uint8)

    with pytest.raises(KeyValidationError):
        scheme.decrypt(ciphertext)


def test_decrypt_rejects_wrong_ciphertext_length(keypair):
    scheme = MRHSCrypto.new(keypair.private_key)
    params = keypair.private_key.parameters

    ciphertext = np.zeros(2 * params.m - 1, dtype=np.uint8)

    with pytest.raises(CiphertextValidationError):
        scheme.decrypt(ciphertext)