import numpy as np

from mrhscrypto.keys import PublicKey, PrivateKey, KeyPair


def test_generate_keypair_returns_keypair(keypair):
    assert isinstance(keypair, KeyPair)
    assert isinstance(keypair.public_key, PublicKey)
    assert isinstance(keypair.private_key, PrivateKey)


def test_key_parameters_match(keypair):
    assert keypair.public_key.parameters == keypair.private_key.parameters


def test_key_shapes_are_correct(keypair):
    params = keypair.public_key.parameters

    assert keypair.public_key.G.shape == (params.n, 2 * params.m)
    assert keypair.private_key.M.shape == (params.n, 2 * params.m)
    assert keypair.private_key.R.shape == (params.n, params.n)


def test_has_private_distinguishes_keys(keypair):
    assert keypair.public_key.has_private() is False
    assert keypair.private_key.has_private() is True


def test_public_key_returns_itself(keypair):
    public_key = keypair.public_key

    assert public_key.public_key() is public_key


def test_private_key_can_derive_public_key(keypair):
    derived_public_key = keypair.private_key.public_key()

    assert isinstance(derived_public_key, PublicKey)
    assert derived_public_key.parameters == keypair.private_key.parameters

    np.testing.assert_array_equal(
        derived_public_key.G,
        keypair.public_key.G,
    )