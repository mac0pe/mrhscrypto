import numpy as np
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


def generate_nonzero_vector():
    while True:
        v = np.random.randint(0, 2, size=2, dtype=np.uint8)
        if np.any(v):
          return v 


def generate_nonzero_vector_block(m):
    blocks = [generate_nonzero_vector() for _ in range(m)]
    return np.concatenate(blocks)


def generate_invertible_matrix(n):
    while True:
        R = np.random.randint(0, 2, size=(n, n), dtype=np.uint8)
        if is_invertible_gf2(R):
            return R