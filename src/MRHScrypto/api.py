import hashlib
from solver import solve_one_sparse
import time, numpy as np
LAMBDA = 128


# prepisane
def generate_full_rank_block(n):
    while True:
        M = np.zeros((n, 2), dtype=np.uint8)
        a1 = np.random.randint(0, n)
        a2 = np.random.randint(0, n)
        if a1 == a2:
            continue
        M[a1,0] = 1
        M[a2,1] = 1
        return M
        

def generate_full_rank_block_matrix(n, m):
    while True:
        M = generate_full_rank_block(n)
        for _ in range(m - 1):
            M = np.hstack((M, generate_full_rank_block(n)))
        if rank_gf2(M) == n:
            return M

# prepisane
def generate_nonzero_vector():
    while True:
        v = np.random.randint(0, 2, size=2, dtype=np.uint8)
        if np.any(v):
          return v 
         
# prepisane
def generate_nonzero_vector_block(m):
    blocks = [generate_nonzero_vector() for _ in range(m)]
    return np.concatenate(blocks)

def rank_gf2(A):
    A = A.copy().astype(np.uint8) % 2
    rows, cols = A.shape
    rank = 0
    col = 0

    for r in range(rows):
        while col < cols and not np.any(A[r:, col]):
            col += 1
        if col == cols:
            break

        pivot = r + np.argmax(A[r:, col])
        A[[r, pivot]] = A[[pivot, r]]

        for i in range(rows):
            if i != r and A[i, col]:
                A[i] ^= A[r]

        rank += 1
        col += 1

    return rank

def is_invertible_gf2(A):
    return A.shape[0] == A.shape[1] and rank_gf2(A) == A.shape[0]
         
# spravene
def generate_invertible_matrix(n):
    while True:
        R = np.random.randint(0, 2, size=(n, n), dtype=np.uint8)
        if is_invertible_gf2(R):
            return R

def inverse_gf2(A):
    A = A.copy().astype(np.uint8) % 2
    n = A.shape[0]

    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix must be square.")

    I = np.eye(n, dtype=np.uint8)
    aug = np.hstack((A, I))

    row = 0
    for col in range(n):
        pivot = None
        for r in range(row, n):
            if aug[r, col] == 1:
                pivot = r
                break

        if pivot is None:
            raise ValueError("Matrix is not invertible over GF(2).")

        if pivot != row:
            aug[[row, pivot]] = aug[[pivot, row]]

        for r in range(n):
            if r != row and aug[r, col] == 1:
                aug[r] ^= aug[row]

        row += 1

    return aug[:, n:]

# spravene skontrolovat inverziu R
def generate_key_pair(n, m):
    M = generate_full_rank_block_matrix(n, m)
    R = generate_invertible_matrix(n)
    R_inverted = inverse_gf2(R)
    private_key = (M, R)
    public_key = (R_inverted @ M) % 2
    return (private_key, public_key)

# spravene
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


# spravene
def generate_plaintext(n):
    message = np.random.randint(0, 2, size=LAMBDA, dtype=np.uint8)
    tag = hash_from_message(message, n - LAMBDA)
    return np.concatenate((message, tag))


# spravene
def encrypt(message, public_key):
    v = generate_nonzero_vector_block(public_key.shape[1] // 2)
    return ((message @ public_key) % 2) ^ v

# spravene
def check_tag(plaintext):
    message = plaintext[:LAMBDA]
    tag = plaintext[LAMBDA:]
    real_tag = hash_from_message(message, len(tag))
    return np.array_equal(real_tag, tag)

# prerobene
def decrypt(ciphertext, private_key):
    candidates = solve_one_sparse(ciphertext, private_key[0])
    for candidate in candidates:
        plaintext = (candidate @ private_key[1]) % 2
        if check_tag(plaintext):
            print("success")
            return plaintext
    return None


c1 = 1.26
c2 = 4.32
n = int(round(c1 * LAMBDA / 8) * 8)
m = int(round(c2 * c1 * LAMBDA / 4) * 4)
start = time.time()

message = generate_plaintext(n)

private_key, public_key = generate_key_pair(n, m)
encrypted_message = encrypt(message, public_key)
decrypted_message = decrypt(encrypted_message, private_key)

endd = time.time()

if decrypted_message is not None:
    print("decryption successful")
    print("matches original:", np.array_equal(message, decrypted_message))
else:
    print("decryption failed")

#print("total time:", endd - start)