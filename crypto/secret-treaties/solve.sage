#!/usr/bin/env sage-run
"""Low-density subset-sum attack for Secret Treaties.

Run from this directory with:
    sage-run solve.sage [pubkey.txt ciphertext.txt]

The (n+1)-dimensional lattice contains the short vector
    (2*x_0-1, ..., 2*x_(n-1)-1, 0)
for any solution x in {0,1}^n to sum(a_i*x_i) = target.
"""

import sys


def numbers(path):
    with open(path) as f:
        return [ZZ(line.strip()) for line in f
                if line.strip() and not line.lstrip().startswith("#")]


def bits_to_bytes(bits):
    assert len(bits) % 8 == 0
    return bytes(sum(bits[i + j] << (7-j) for j in range(8))
                 for i in range(0, len(bits), 8))


def scan_basis(reduced, a, target):
    n = len(a)
    for row in reduced.rows():
        if row[n] == 0 and all(abs(row[j]) == 1 for j in range(n)):
            # row may be either the desired vector or its negation.
            for v in (row, -row):
                bits = [(ZZ(v[j]) + 1) // 2 for j in range(n)]
                if all(bit in (0, 1) for bit in bits) and \
                   sum(ai * bit for ai, bit in zip(a, bits)) == target:
                    return bits
    return None


def solve_target(a, target):
    n = len(a)
    B = matrix(ZZ, n + 1, n + 1)
    for i, ai in enumerate(a):
        B[i, i] = 2
        B[i, n] = 2 * ai
    for j in range(n):
        B[n, j] = 1
    B[n, n] = 2 * target

    reduced = B.LLL(delta=0.999)
    bits = scan_basis(reduced, a, target)
    if bits is None:
        # Only the final, padded block needs this on the supplied instance.
        reduced = reduced.BKZ(block_size=20)
        bits = scan_basis(reduced, a, target)
    if bits is None:
        raise RuntimeError("lattice reduction did not expose a valid solution")
    return bits


base = "attachments/files/"
pub_path = sys.argv[1] if len(sys.argv) > 1 else base + "pubkey.txt"
ct_path = sys.argv[2] if len(sys.argv) > 2 else base + "ciphertext.txt"

a = numbers(pub_path)
targets = numbers(ct_path)
assert len(a) == 72

# Flag bytes are printable ASCII (and the padding bytes are NUL), so bit 7 of
# every byte is known to be zero.  Removing those nine entries lowers the
# subset-sum density from 72/96 = 0.75 to 63/96 = 0.656, enough for this
# instance to reduce cleanly.
active_indices = [i for i in range(len(a)) if i % 8 != 0]
active_a = [a[i] for i in active_indices]

blocks = []
for blockno, target in enumerate(targets):
    active_bits = solve_target(active_a, target)
    bits = [0] * len(a)
    for i, bit in zip(active_indices, active_bits):
        bits[i] = bit
    block = bits_to_bytes(bits)
    print(f"block {blockno}: {block!r}")
    blocks.append(block)

plaintext = b"".join(blocks)
print(f"plaintext: {plaintext!r}")
try:
    print(plaintext.decode("ascii"))
except UnicodeDecodeError:
    pass
