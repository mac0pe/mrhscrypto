from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class PublicKey:
    G: np.ndarray

@dataclass(frozen=True)
class PrivateKey:
    M: np.ndarray
    R: np.ndarray

@dataclass(frozen=True)
class KeyPair:
    public_key: PublicKey
    private_key: PrivateKey

@dataclass(frozen=True)
class MRHSParameters:
    d: int
    security: int
    n: int
    m: int