import hashlib
import numpy as np

def check_tag(plaintext, security):
    message = plaintext[:security]
    tag = plaintext[security:]
    real_tag = hash_from_message(message, len(tag))
    return np.array_equal(real_tag, tag)

def hash_from_message(message, tag_len):
    m_int = int("".join(str(int(b)) for b in message), 2)

    num_bytes = len(message) // 8
    m_bytes = m_int.to_bytes(num_bytes, 'big')

    digest = hashlib.sha256(m_bytes).digest()

    tag_len_bytes = tag_len // 8
    tag_bytes = digest[:tag_len_bytes]
    bits = []
    for byte in tag_bytes:
        for i in range(8):
            bits.append((byte >> (7-i)) & 1)

    return np.array(bits, dtype=np.uint8)
