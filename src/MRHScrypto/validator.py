import numpy as np

def precompute_forbidden_positions(ciphertext):
    m = len(ciphertext) // 2
    forbidden = []
    for i in range(m):
        ci = ciphertext[2*i:2*i+2]
        forbidden.append((2*i, 2*i+1, ci[0], ci[1]))
    return forbidden

def is_valid(y, forbidden):
    for pos0, pos1, c0, c1 in forbidden:
        if y[pos0] == c0 and y[pos1] == c1:
            return False
    return True

def validate_all_solutions(x_base, M, ciphertext):
    undecided = []

    x_base = list(x_base)  
    for i in range(len(x_base)):
        if x_base[i] is None:
            undecided.append(i)
            x_base[i] = 0

    x_vec = np.array(x_base, dtype=np.uint8)
    y = (x_vec @ M) % 2

    forbidden = precompute_forbidden_positions(ciphertext)

    valid = []
    if is_valid(y, forbidden):
        valid.append(x_vec.copy())

    gray_code_prev = 0
    for t in range(1, 1 << len(undecided)):
        gray_code = t ^ (t >> 1)
        bit_flipped = gray_code ^ gray_code_prev
        idx_undecided = bit_flipped.bit_length() - 1
        idx_x = undecided[idx_undecided]

        x_vec[idx_x] ^= 1
        y ^= M[idx_x]

        if is_valid(y, forbidden):
            valid.append(x_vec.copy())

        gray_code_prev = gray_code

    print("number of valid solutions:", len(valid), "out of", 1 << len(undecided))
    return valid
    

