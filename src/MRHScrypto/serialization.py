from pathlib import Path
import numpy as np
from .keys import PrivateKey, PublicKey
from .parameters import MRHSParameters
from .exceptions import KeyValidationError, KeySerializationError


def _validate_path(path, *, for_writing: bool) -> Path:
    path = Path(path)

    if path.suffix != ".npz":
        raise KeySerializationError("Key file must have .npz extension.")

    if for_writing:
        if path.parent and not path.parent.exists():
            raise KeySerializationError(
                f"Directory does not exist: {path.parent}"
            )
    else:
        if not path.exists():
            raise KeySerializationError(f"Key file does not exist: {path}")

        if not path.is_file():
            raise KeySerializationError(f"Path is not a file: {path}")

    return path


def save_public_key(key:PublicKey, path):
    path = _validate_path(path, for_writing=True)

    try:
        np.savez_compressed(
            path,
            key_type="public",
            format_version=1,
            d=key.parameters.d,
            security=key.parameters.security,
            n=key.parameters.n,
            m=key.parameters.m,
            G=key.G,
        )
    except OSError as error:
        raise KeySerializationError(
            f"Failed to save public key to file: {path}"
        ) from error
    
def save_private_key(key:PrivateKey, path):
    path = _validate_path(path, for_writing=True)
    try:
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
    except OSError as error:
        raise KeySerializationError(
            f"Failed to save private key to file: {path}"
        ) from error    

def load_key(path):
    path = _validate_path(path, for_writing=False)
    
    try:
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
    except OSError as error:
        raise KeySerializationError(
            f"Failed to load key from file: {path}"
        ) from error  
    

    

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