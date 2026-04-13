import numpy as np

def rank_gf2(A):
    A = A.copy().astype(np.uint8) % 2
    rows, cols = A.shape
    rank = 0
    col = 0

    for r in range(rows):
        # Hladame pivota
        # Ak niesme v poslednom stlpci a zaroven sa od riadku r dole v tom stlpci nenachadza ziadna jednotka 
        while col < cols and not np.any(A[r:, col]):
            # tak sa posunime o stlpec dalej
            col += 1
        # ak sme minuly vsetky stlpce tak koniec
        if col == cols:
            break
        
        # pivot sa nachadza v stlcpi col na indexe r + pozicia v stlpci od riadku r dole 
        pivot = r + np.argmax(A[r:, col])
        # swapneme aktulany riadok s riadok s pivotom
        A[[r, pivot]] = A[[pivot, r]]

        # ak mame pivota musime eliminovat vsetky jednotky v tom stlpci kde je pivot
        for i in range(rows):
            if i != r and A[i, col]:
                A[i] ^= A[r]

        # kazdy pivot zvysi ran o 1
        rank += 1
        # posuvame sa hladat pivota do dalsieho stlpca
        col += 1

    return rank

def is_invertible_gf2(A):
    # aby bola invertibilna musi byt stvorcova a plnej hodnosti

    rows, cols = A.shape

    if rows != cols:
        return False

    if rank_gf2(A) != rows:
        return False

    return True


def inverse_gf2(A):
    A = A.copy().astype(np.uint8) % 2
    n = A.shape[0]

    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix must be square.")

    # k matici pripojimejednotkovu maticu klasicky postup
    I = np.eye(n, dtype=np.uint8)
    aug = np.hstack((A, I))

    # ideme robit gausovu eliminaciu
    row = 0
    # prechadzame cez vsetky stlpce a hladame v nich pivotov
    for col in range(n):
        pivot = None
        for r in range(row, n):
            if aug[r, col] == 1:
                pivot = r
                break

        if pivot is None:
            raise ValueError("Matrix is not invertible over GF(2).")

        # swapneme riadok s pivotom na aktualny riadok bez pivota
        if pivot != row:
            aug[[row, pivot]] = aug[[pivot, row]]

        # eliminujeme jednotky v stlpci s pivotom
        for r in range(n):
            if r != row and aug[r, col] == 1:
                aug[r] ^= aug[row]

        row += 1
    # vraciame spat pravu cast kde sa z jednotkovej matice stala invertovana
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