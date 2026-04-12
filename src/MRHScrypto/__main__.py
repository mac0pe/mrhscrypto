import numpy as np
from .scheme import MRHSCrypto

def main():
    scheme = MRHSCrypto(d=1, security=128)
    keypair = scheme.generate_key_pair()
    message = np.random.randint(0, 2, size=scheme.parameters.security, dtype=np.uint8)
    ciphertext = scheme.encrypt(message, keypair.public_key)
    decrypted = scheme.decrypt(ciphertext, keypair.private_key)
    
if __name__ == "__main__":
    main()