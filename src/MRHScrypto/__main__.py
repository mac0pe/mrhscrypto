import base64
from mrhscrypto import MRHSCrypto

def main():
    keypair = MRHSCrypto.generate_keypair(d=1, security=128)

    encryptor = MRHSCrypto.new(keypair.public_key)
    decryptor = MRHSCrypto.new(keypair.private_key)

    message = b"1234567890abcdef"

    ciphertext = encryptor.encrypt(message)
    ciphertext_b64 = base64.b64encode(ciphertext).decode("ascii")

    decoded_ciphertext = base64.b64decode(ciphertext_b64.encode("ascii"))
    decrypted = decryptor.decrypt(decoded_ciphertext)

    print("Message:", message.decode("utf-8"))
    print("Ciphertext Base64:", ciphertext_b64)
    print("Decrypted:", decrypted.decode("utf-8"))
    print("Matches:", decrypted == message)

if __name__ == "__main__":
    main()