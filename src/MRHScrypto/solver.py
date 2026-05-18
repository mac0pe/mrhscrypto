from mrhscrypto.exceptions import DecryptionError
import time, numpy as np
from .validator import validate_all_solutions

def get_index_of_one(col):
    return np.argmax(col)

def lit_id(idx, bit):  # bit in {0,1}
    return 2*idx + bit


def boolean_transitive_closure(GM):
    N = GM.shape[0]

    rows = [0] * N
    for i in range(N):
        mask = 0
        r = GM[i]
        for j, val in enumerate(r):
            if int(val) != 0:
                mask |= (1 << j)
        mask |= (1 << i)
        rows[i] = mask

    for k in range(N):
        rk = rows[k]
        mk = 1 << k
        for i in range(N):
            if rows[i] & mk:
                rows[i] |= rk

    for i in range(N):
        mask = rows[i]
        for j in range(N):
            GM[i, j] = 1 if (mask >> j) & 1 else 0

    return GM


def get_graph_matrix_warshall(ciphertext, M):
    m = M.shape[1]
    n = M.shape[0]
    GM = np.eye(2 * n, dtype=np.uint8)

    for i in range(0, m, 2):
        u = get_index_of_one(M[:, i])
        v = get_index_of_one(M[:, i + 1])
        a = int(ciphertext[i])
        b = int(ciphertext[i + 1])

        from_id = lit_id(u, a)          # node for (x_u = a)
        to_id   = lit_id(v, b ^ 1)      # node for (x_v = b^1)
        GM[from_id, to_id] = 1

        from_id2 = lit_id(v, b)         # (x_v = b)
        to_id2   = lit_id(u, a ^ 1)     # (x_u = a^1)
        GM[from_id2, to_id2] = 1

    GM = boolean_transitive_closure(GM)
    return GM


def get_solutions(GM):
    n = GM.shape[0] // 2
    x = [None] * n
    undecidable_count = 0

    for i in range(n):
        s1 = GM[2 * i + 1, 2 * i]
        s2 = GM[2 * i, 2 * i + 1]

        if s1 == 0 and s2 == 0:
            x[i] = None
            undecidable_count += 1
        elif s1 == 1 and s2 == 1:
            raise ValueError(f"Conflict for variable x[{i}]")
        else:
            x[i] = 0 if s1 == 1 else 1

    return x


def solve_one_sparse(ciphertext, M, validate_solutions=False):
    GM = get_graph_matrix_warshall(ciphertext, M)
    x = get_solutions(GM)
    if len(x) > 15:
        raise DecryptionError("Too many possible solutions to brute-force")
    valid = validate_all_solutions(x, M, ciphertext)

    return valid

