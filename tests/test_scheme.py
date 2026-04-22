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


def test_encrypt_with_public_key_returns_bytes(keypair, message_128):
    encryptor = MRHSCrypto.new(keypair.public_key)

    ciphertext = encryptor.encrypt(message_128)

    assert isinstance(ciphertext, bytes)


def test_encrypt_with_private_key_returns_bytes(keypair, message_128):
    encryptor = MRHSCrypto.new(keypair.private_key)

    ciphertext = encryptor.encrypt(message_128)

    assert isinstance(ciphertext, bytes)


def test_encrypt_rejects_wrong_message_length(keypair):
    encryptor = MRHSCrypto.new(keypair.public_key)

    wrong_message = b"short"

    with pytest.raises(MessageValidationError):
        encryptor.encrypt(wrong_message)


def test_encrypt_rejects_non_bytes_message(keypair):
    encryptor = MRHSCrypto.new(keypair.public_key)

    with pytest.raises(MessageValidationError):
        encryptor.encrypt("not bytes")


def test_public_key_cannot_decrypt(keypair, message_128):
    encryptor = MRHSCrypto.new(keypair.public_key)
    ciphertext = encryptor.encrypt(message_128)

    with pytest.raises(KeyValidationError):
        encryptor.decrypt(ciphertext)


def test_decrypt_rejects_wrong_ciphertext_length(keypair):
    decryptor = MRHSCrypto.new(keypair.private_key)

    wrong_ciphertext = b"wrong"

    with pytest.raises(CiphertextValidationError):
        decryptor.decrypt(wrong_ciphertext)


def test_decrypt_rejects_non_bytes_ciphertext(keypair):
    decryptor = MRHSCrypto.new(keypair.private_key)

    with pytest.raises(CiphertextValidationError):
        decryptor.decrypt("not bytes")