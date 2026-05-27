from dataclasses import dataclass
from .parameters import MRHSParameters
from .matrices import is_invertible_gf2, inverse_gf2
from .exceptions import KeyValidationError
from abc import ABC, abstractmethod
import numpy as np

@dataclass(frozen=True)
class Key(ABC):
    parameters: MRHSParameters

    @abstractmethod
    def save(self, path):
        pass

    @abstractmethod
    def has_private(self) -> bool:
        pass
    
    @abstractmethod
    def public_key(self) -> "PublicKey":
        pass

@dataclass(frozen=True)
class PublicKey(Key):
    G: np.ndarray

    def save(self, path):
        from .serialization import save_public_key
        save_public_key(self, path)
    

    def has_private(self) -> bool:
        return False

    def public_key(self) -> "PublicKey":
        return self

@dataclass(frozen=True)
class PrivateKey(Key):
    M: np.ndarray
    R: np.ndarray

    def save(self, path):
        from .serialization import save_private_key
        save_private_key(self, path)


    def has_private(self) -> bool:
        return True
    

    def public_key(self) -> PublicKey:
        M = self.M
        R = self.R
        if not is_invertible_gf2(R):
            raise KeyValidationError("Non valid private key.")
        G = (inverse_gf2(R) @ M) % 2
        public_key = PublicKey(parameters=self.parameters, G=G)
        return public_key


@dataclass(frozen=True)
class KeyPair:
    public_key: PublicKey
    private_key: PrivateKey

