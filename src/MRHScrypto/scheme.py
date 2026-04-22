from .keys import KeyPair, PrivateKey, PublicKey, Key
from .parameters import MRHSParameters
from .exceptions import CiphertextValidationError, ParameterError, UnsupportedSolverError, KeyValidationError, MessageValidationError
from .matrices import generate_nonzero_vector_block, generate_full_rank_block_matrix, generate_invertible_matrix, inverse_gf2
from .hashing import check_tag, hash_from_message
from .solver import solve_one_sparse
from .serialization import load_key
import numpy as np

class MRHSCrypto:

    def __init__(self, key: Key):
        self.key = key


    @classmethod
    def new(cls, key: Key):
        return cls(key)


    def _build_parameters(d:int, security:int) -> MRHSParameters:
        c1 = 1.26
        c2 = 4.32

        n = int(round(c1 * security / 8) * 8)
        m = int(round(c2 * c1 * security / 4) * 4)

        return MRHSParameters(d=d,security=security,n=n,m=m,)


    @staticmethod
    def generate_keypair(d:int,security:int) -> KeyPair:
        if not isinstance(d, int) or d != 1:
            raise ParameterError("Parameter d > 1 is currently unsupported.")
        
        if security != 128 and security != 256:
            raise ParameterError("Security parameter must be either 128 or 256.")
        
        parameters = MRHSCrypto._build_parameters(d, security)

        n = parameters.n
        m = parameters.m
        M = generate_full_rank_block_matrix(n, m)
        R = generate_invertible_matrix(n)
        R_inverted = inverse_gf2(R)
        private_key = PrivateKey(parameters,M, R)
        G = (R_inverted @ M) % 2
        public_key = PublicKey(parameters,G)

        return KeyPair(public_key,private_key)
    

    # TODO zaobalit spravu do nejakeho objektu alebo tak aby to nebol numpy vector
    def encrypt(self, message):
        public_key = self.key.public_key()

        if len(message) != public_key.parameters.security:
            raise MessageValidationError(
                f"Message has invalid length {len(message)}, "
                f"expected {public_key.parameters.security}."
            )
        tag = hash_from_message(message, public_key.parameters.n - public_key.parameters.security)
        plaintext = np.concatenate((message, tag))
        v = generate_nonzero_vector_block(public_key.parameters.m)
        return ((plaintext @ public_key.G) % 2) ^ v
    

    # TODO ak bude moc volnych premennych tak ako to spravit? Nemozeme len tak zahodit kluc a vymenit
    # hodit nejaky error alebo poskusat mozno bude stacit pregenerovat ked sa da ta random cast 
    def decrypt(self, ciphertext): 
        if not self.key.has_private():
            raise KeyValidationError("Key must be a PrivateKey instance.")

        if len(ciphertext) != 2 * self.key.parameters.m:
            raise CiphertextValidationError(
                f"Ciphertext has invalid length {len(ciphertext)}, "
                f"expected {2 * self.key.parameters.m}."
            ) 
        solver = self._get_solver()
        candidates = solver(ciphertext, self.key.M)
        for candidate in candidates:
            plaintext = (candidate @ self.key.R) % 2
            if check_tag(plaintext, self.key.parameters.security):
                print("success")
                return plaintext[:self.key.parameters.security]
        return None


    def _get_solver(self):
        if self.key.parameters.d == 1:
            return solve_one_sparse
        raise UnsupportedSolverError(f"No solver implemented for d={self.key.parameters.d}")
    

    @staticmethod
    def import_key(path) -> Key:
        key = load_key(path)
        return key
