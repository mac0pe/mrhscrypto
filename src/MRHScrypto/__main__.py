import numpy as np
from .scheme import MRHSCrypto

def main():
    scheme = MRHSCrypto(d=1, security=128)

    print("Generating keypair...")
    keypair = scheme.generate_keypair()

    print("Saving keys...")
    keypair.public_key.save("public_key.npz")
    keypair.private_key.save("private_key.npz")

    print("Loading keys...")
    public_key = scheme.load_public_key("public_key.npz")
    private_key = scheme.load_private_key("private_key.npz")

    message = np.random.randint(0, 2, size=scheme.parameters.security, dtype=np.uint8)
    print("message:", message)

    ciphertext = scheme.encrypt(message, public_key)
    print("ciphertext:", ciphertext)

    recovered_message = scheme.decrypt(ciphertext, private_key)

    print("recovered:", recovered_message)
    print("matches:", np.array_equal(message, recovered_message))


if __name__ == "__main__":
    main()