from .keys import KeyPair, PrivateKey, PublicKey
from .parameters import MRHSParameters
from .exceptions import CiphertextValidationError, ParameterError, UnsupportedSolverError, KeyValidationError, MessageValidationError
from .matrices import generate_nonzero_vector_block, generate_full_rank_block_matrix, generate_invertible_matrix, inverse_gf2
from .hashing import check_tag, hash_from_message
from .solver import solve_one_sparse
from .serialization import load_key, load_private_key, load_public_key
import numpy as np

class MRHSCrypto:
    def __init__(self,d,security):
        # TODO neskor naprílkad d <= 0 and d >= 4
        if not isinstance(d, int) or d != 1:
            raise ParameterError("Parameter d > 1 is currently unsupported.")
        
        if security != 128 and security != 256:
            raise ParameterError("Security parameter must be either 128 or 256.")
        
        self.parameters = self._build_parameters(d, security)
    

    def _build_parameters(self,d:int, security:int) -> MRHSParameters:
        c1 = 1.26
        c2 = 4.32

        n = int(round(c1 * security / 8) * 8)
        m = int(round(c2 * c1 * security / 4) * 4)

        return MRHSParameters(d=d,security=security,n=n,m=m,)


    # TODO generovanie v zavislosti od velkosti d ---- netreba 
    # TODO co stou hodnostou kedze pri parnom d nemoze byt plna? ----- staci d=1
    def generate_keypair(self):
        n = self.parameters.n
        m = self.parameters.m
        M = generate_full_rank_block_matrix(n, m)
        R = generate_invertible_matrix(n)
        R_inverted = inverse_gf2(R)
        private_key = PrivateKey(self.parameters,M, R)
        G = (R_inverted @ M) % 2
        public_key = PublicKey(self.parameters,G)
        return KeyPair(public_key,private_key)


    # TODO prerobit tak aby mohla byt message hocijakej dlzky ---- netreba
    # aktualne iba dlzky ako security 
    # TODO ako spravit ten padding? Pri 128 ak pridam na zaciatok +- 6 bitov ktoré budu drzat kolko je paddingu
         # potom nejakých par bitov paddingu napriklad 10 nech je to zarovnane s hashom na bajty tak na hash ostane 16bitov 
         # kolizia bude teda plus minus 2^16? pri vacsom pocte volnych premennych to bude uz problem
    def encrypt(self, message, public_key : PublicKey):
        if not isinstance(public_key, PublicKey):
            raise KeyValidationError("public_key must be a PublicKey instance.")

        self._validate_key_parameters(public_key.parameters)

        if len(message) != self.parameters.security:
            raise MessageValidationError(
                f"Message has invalid length {len(message)}, "
                f"expected {self.parameters.security}."
            )
        tag = hash_from_message(message, self.parameters.n - self.parameters.security)
        plaintext = np.concatenate((message, tag))
        v = generate_nonzero_vector_block(self.parameters.m)
        return ((plaintext @ public_key.G) % 2) ^ v
    
    # TODO ak bude moc volnych premennych tak ako to spravit? Nemozeme len tak zahodit kluc a vymenit
    # hodit nejaky error alebo poskusat mozno bude stacit pregenerovat ked sa da ta random cast 
    def decrypt(self, ciphertext, private_key : PrivateKey): 
        if not isinstance(private_key, PrivateKey):
            raise KeyValidationError("private_key must be a PrivateKey instance.")

        self._validate_key_parameters(private_key.parameters)

        if len(ciphertext) != 2 * self.parameters.m:
            raise CiphertextValidationError(
                f"Ciphertext has invalid length {len(ciphertext)}, "
                f"expected {2 * self.parameters.m}."
            ) 
        solver = self._get_solver()
        candidates = solver(ciphertext, private_key.M)
        for candidate in candidates:
            plaintext = (candidate @ private_key.R) % 2
            if check_tag(plaintext, self.parameters.security):
                print("success")
                return plaintext[:self.parameters.security]
        return None


    def _get_solver(self):
        if self.parameters.d == 1:
            return solve_one_sparse
        raise UnsupportedSolverError(f"No solver implemented for d={self.parameters.d}")
    

    def _validate_key_parameters(self, key_parameters):
        if key_parameters != self.parameters:
            raise KeyValidationError("Given key parameters do not match this MRHSCrypto instance."
                                     f"Given: d={key_parameters.parameters.d}, security={key_parameters.parameters.security},"
                                     f"Expected: d={self.parameters.d}, security={self.parameters.security}," 
                                    )

    
    # TODO spravit ako staticku funkciu racej?
    def load_key(self, path):
        key = load_key(path)
        self._validate_key_parameters(key.parameters)
        return key

    def load_public_key(self, path):
        key = load_public_key(path)
        self._validate_key_parameters(key.parameters)
        return key

    def load_private_key(self, path):
        key = load_private_key(path)
        self._validate_key_parameters(key.parameters)
        return key
