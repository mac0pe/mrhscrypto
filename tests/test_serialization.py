import numpy as np
import pytest

from mrhscrypto import MRHSCrypto
from mrhscrypto.keys import PublicKey, PrivateKey
from mrhscrypto.exceptions import KeySerializationError, KeyValidationError


def test_save_and_load_public_key(keypair, tmp_path):
    path = tmp_path / "public_key.npz"

    keypair.public_key.save(path)
    loaded_key = MRHSCrypto.import_key(path)

    assert isinstance(loaded_key, PublicKey)
    assert loaded_key.parameters == keypair.public_key.parameters
    assert loaded_key.has_private() is False

    np.testing.assert_array_equal(
        loaded_key.G,
        keypair.public_key.G,
    )


def test_save_and_load_private_key(keypair, tmp_path):
    path = tmp_path / "private_key.npz"

    keypair.private_key.save(path)
    loaded_key = MRHSCrypto.import_key(path)

    assert isinstance(loaded_key, PrivateKey)
    assert loaded_key.parameters == keypair.private_key.parameters
    assert loaded_key.has_private() is True

    np.testing.assert_array_equal(
        loaded_key.M,
        keypair.private_key.M,
    )

    np.testing.assert_array_equal(
        loaded_key.R,
        keypair.private_key.R,
    )


def test_loaded_private_key_can_derive_public_key(keypair, tmp_path):
    path = tmp_path / "private_key.npz"

    keypair.private_key.save(path)
    loaded_private_key = MRHSCrypto.import_key(path)

    derived_public_key = loaded_private_key.public_key()

    np.testing.assert_array_equal(
        derived_public_key.G,
        keypair.public_key.G,
    )


def test_save_rejects_non_npz_extension(keypair, tmp_path):
    path = tmp_path / "public_key.txt"

    with pytest.raises(KeySerializationError):
        keypair.public_key.save(path)


def test_load_rejects_missing_file(tmp_path):
    path = tmp_path / "missing_key.npz"

    with pytest.raises(KeySerializationError):
        MRHSCrypto.import_key(path)


def test_load_rejects_unknown_key_type(tmp_path):
    path = tmp_path / "bad_key.npz"

    np.savez_compressed(
        path,
        key_type="unknown",
        d=1,
        security=128,
        n=160,
        m=696,
    )

    with pytest.raises(KeyValidationError):
        MRHSCrypto.import_key(path)