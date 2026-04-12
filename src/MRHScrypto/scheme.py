from .mrhs_types import MRHSParameters, KeyPair, PrivateKey, PublicKey
from .matrices import generate_nonzero_vector_block, generate_full_rank_block_matrix, generate_invertible_matrix, inverse_gf2
from .hashing import check_tag, hash_from_message
from .solver import solve_one_sparse
import numpy as np

class MRHSCrypto:
    def __init__(self,d,security):
        self.parameters = self._build_parameters(d, security)
    
    def _build_parameters(self,d:int, security:int) -> MRHSParameters:
        c1 = 1.26
        c2 = 4.32

        n = int(round(c1 * security / 8) * 8)
        m = int(round(c2 * c1 * security / 4) * 4)

        return MRHSParameters(d=d,security=security,n=n,m=m,)


    # TODO generovanie v zavislosti od velkosti d
    def generate_key_pair(self):
        n = self.parameters.n
        m = self.parameters.m
        M = generate_full_rank_block_matrix(n, m)
        R = generate_invertible_matrix(n)
        R_inverted = inverse_gf2(R)
        private_key = PrivateKey(M, R)
        G = (R_inverted @ M) % 2
        public_key = PublicKey(G)
        return KeyPair(public_key,private_key)


    # TODO prerobit tak aby mohla byt message hocijakej dlzky 
    # aktualne iba dlzky ako security
    # TODO popridavat chcecky ci je kluc kompatibilny so security a tak
    def encrypt(self, message, public_key : PublicKey):
        tag = hash_from_message(message, self.parameters.n - self.parameters.security)
        plaintext = np.concatenate((message, tag))
        v = generate_nonzero_vector_block(self.parameters.m)
        return ((plaintext @ public_key.G) % 2) ^ v
    
    # TODO ak bude moc volnych premennych tak ako to spravit? Nemozeme len tak zahodit kluc a vymenit
    # TODO rozhodovanie aky solver pouzit v zavislosti od d, mozno solver spravit ako polymorfizmus
    def decrypt(self, ciphertext, private_key : PrivateKey):
        candidates = solve_one_sparse(ciphertext, private_key.M)
        for candidate in candidates:
            plaintext = (candidate @ private_key.R) % 2
            if check_tag(plaintext, self.parameters.security):
                print("success")
                return plaintext
        return None


    #def save_key():

    #def load_key():
