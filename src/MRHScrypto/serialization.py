import numpy as np
from .keys import PrivateKey, PublicKey
from .parameters import MRHSParameters
from .exceptions import KeyValidationError

def save_public_key(key:PublicKey, path):
    np.savez_compressed(
    path,
    key_type="public",
    d=key.parameters.d,
    security=key.parameters.security,
    n=key.parameters.n,
    m=key.parameters.m,
    G=key.G,
    )
    
def save_private_key(key:PrivateKey, path):
    np.savez_compressed(
    path,
    key_type="private",
    d=key.parameters.d,
    security=key.parameters.security,
    n=key.parameters.n,
    m=key.parameters.m,
    M = key.M,
    R = key.R
    )

def load_key(path):
    data = np.load(path, allow_pickle=False)

    key_type = str(data["key_type"])
    params = MRHSParameters(
        d=int(data["d"]),
        security=int(data["security"]),
        n=int(data["n"]),
        m=int(data["m"]),
    )

    if key_type == "public":
        return PublicKey(
            G=data["G"],
            parameters=params,
        )

    if key_type == "private":
        return PrivateKey(
            M=data["M"],
            R=data["R"],
            parameters=params,
        )

    raise KeyValidationError(f"Unknown key type: {key_type}")

def load_public_key(path):
    key = load_key(path)
    if not isinstance(key, PublicKey):
        raise KeyValidationError("Expected a public key file.")
    return key


def load_private_key(path):
    key = load_key(path)
    if not isinstance(key, PrivateKey):
        raise KeyValidationError("Expected a private key file.")
    return key