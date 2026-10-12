#!/usr/bin/env python3
"""Solver for CSAW 2026 Quals - Polly.

With no arguments this launches the supplied challenge locally.  Pass HOST and
PORT to use the same solver against a remote instance.
"""

import argparse
import os
import random
import re
import socket
import subprocess
import tempfile
from hashlib import shake_256
from pathlib import Path


MASK64 = (1 << 64) - 1
ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "extracted" / "player" / "main.py"


class Tube:
    def __init__(self, host=None, port=None):
        self.proc = None
        self.sock = None
        self.buf = bytearray()
        if host is None:
            env = os.environ.copy()
            env.setdefault("FLAG", "flag{fake_flag}")
            self.proc = subprocess.Popen(
                ["python3", "-u", str(MAIN)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
        else:
            self.sock = socket.create_connection((host, port))

    def _read(self):
        if self.sock is not None:
            data = self.sock.recv(4096)
        else:
            data = os.read(self.proc.stdout.fileno(), 4096)
        if not data:
            raise EOFError("challenge closed the connection")
        self.buf += data

    def recvuntil(self, marker):
        while True:
            pos = self.buf.find(marker)
            if pos >= 0:
                pos += len(marker)
                result = bytes(self.buf[:pos])
                del self.buf[:pos]
                return result
            self._read()

    def sendline(self, data=b""):
        if isinstance(data, str):
            data = data.encode()
        data += b"\n"
        if self.sock is not None:
            self.sock.sendall(data)
        else:
            self.proc.stdin.write(data)
            self.proc.stdin.flush()

    def close(self):
        if self.sock is not None:
            self.sock.close()
        elif self.proc is not None:
            self.proc.kill()
            self.proc.wait()


def get_parameters(base_nonce):
    material = shake_256(base_nonce).digest(5)
    available = list(range(1, 64))
    shifts = []
    for byte in material[1:]:
        shifts.append(available.pop(byte % len(available)))
    return shifts, material[0] & 1


def transform(state, shifts, num):
    if num == 0:
        state ^= (state << shifts[0]) & MASK64
        state ^= state >> shifts[1]
        state ^= (state << shifts[2]) & MASK64
        state ^= state >> shifts[3]
    else:
        state ^= state >> shifts[0]
        state ^= (state << shifts[1]) & MASK64
        state ^= state >> shifts[2]
        state ^= (state << shifts[3]) & MASK64
    return state & MASK64


def apply_operator(operator, state):
    result = 0
    while state:
        bit = (state & -state).bit_length() - 1
        result ^= operator[bit]
        state &= state - 1
    return result


def build_jumps(shifts, num):
    jumps = [[transform(1 << bit, shifts, num) for bit in range(64)]]
    for _ in range(63):
        op = jumps[-1]
        jumps.append([apply_operator(op, col) for col in op])
    return jumps


def operator_at(x, jumps):
    # Columns of T**x, where T is the xorshift transition.
    columns = [1 << bit for bit in range(64)]
    bit = 0
    while x:
        if x & 1:
            op = jumps[bit]
            columns = [apply_operator(op, col) for col in columns]
        bit += 1
        x >>= 1
    return columns


def low_byte_rows(x, jumps):
    columns = operator_at(x, jumps)
    rows = []
    for output_bit in range(8):
        row = 0
        for seed_bit, col in enumerate(columns):
            if (col >> output_bit) & 1:
                row |= 1 << seed_bit
        rows.append(row)
    return rows


class LinearBasis:
    """Row-echelon GF(2) basis, optionally carrying right-hand sides."""

    def __init__(self):
        self.rows = {}

    def add(self, row, rhs=0):
        while row:
            pivot = row.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = (row, rhs)
                return True
            old_row, old_rhs = self.rows[pivot]
            row ^= old_row
            rhs ^= old_rhs
        if rhs:
            raise ValueError("inconsistent GF(2) equations")
        return False

    @property
    def rank(self):
        return len(self.rows)

    def solution(self):
        if self.rank != 64:
            raise ValueError(f"need rank 64, only have rank {self.rank}")
        value = 0
        # Each row's pivot is its highest set bit, so its other variables have
        # already been determined when pivots are processed low to high.
        for pivot in range(64):
            row, rhs = self.rows[pivot]
            bit = rhs ^ ((row & value).bit_count() & 1)
            value |= bit << pivot
        return value


def choose_queries(jumps, nonce):
    """Choose a small set of x values whose leaked bytes determine the seed."""
    basis = LinearBasis()
    selected = []
    rng = random.Random(int.from_bytes(shake_256(nonce).digest(16), "big"))

    # Random exponents avoid the heavy overlap seen in 64 consecutive 8-bit
    # observations.  On observable instances this normally takes 8-10 queries.
    for attempt in range(256):
        x = 0 if attempt == 0 else rng.getrandbits(64)
        rows = low_byte_rows(x, jumps)
        old_rank = basis.rank
        for row in rows:
            basis.add(row)
        if basis.rank != old_rank:
            selected.append((x, rows))
        if basis.rank == 64:
            return selected

    # This is the approximately 20% failure mode mentioned by the author: the
    # last byte is not a full-rank observation of the 64-bit linear state.
    raise RuntimeError(f"instance is not seed-observable (rank {basis.rank})")


def query_nonce_byte(tube, x, plaintext=b""):
    tube.sendline(str(x))
    tube.recvuntil(b"enter a string to be encrypted: ")
    tube.sendline(plaintext)
    response = tube.recvuntil(b"which seed modifier would you like to use?\n")
    match = re.search(rb"Your nonce byte is: ([0-9a-fA-F]{2})", response)
    if not match:
        raise RuntimeError(f"could not parse oracle response: {response!r}")
    nonce_byte = int(match.group(1), 16)
    ct_match = re.search(rb"Your ciphertext is: ([0-9a-fA-F]+)", response)
    ciphertext = bytes.fromhex(ct_match.group(1).decode()) if ct_match else None
    return nonce_byte, ciphertext


def recover_seed(tube, queries):
    equations = LinearBasis()
    for number, (x, rows) in enumerate(queries, 1):
        leak, _ = query_nonce_byte(tube, x)
        for bit, row in enumerate(rows):
            equations.add(row, (leak >> bit) & 1)
        print(f"[+] oracle query {number:2d}/{len(queries)}: x={x:#018x}, byte={leak:02x}")
    return equations.solution()


def find_collision(seed, target, shifts, num):
    """Compile a tiny optimized loop and find x with low24(T**x seed)=target."""
    operations = (
        f"s ^= s << {shifts[0]}; s ^= s >> {shifts[1]}; "
        f"s ^= s << {shifts[2]}; s ^= s >> {shifts[3]};"
        if num == 0
        else
        f"s ^= s >> {shifts[0]}; s ^= s << {shifts[1]}; "
        f"s ^= s >> {shifts[2]}; s ^= s << {shifts[3]};"
    )
    source = f"""
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
int main(void) {{
    uint64_t s = UINT64_C(0x{seed:016x});
    const uint32_t target = UINT32_C(0x{target:06x});
    for (uint64_t x = 0; ; ++x) {{
        if ((s & UINT32_C(0xffffff)) == target) {{
            printf("%" PRIu64 "\\n", x);
            return 0;
        }}
        {operations}
        if (x == UINT64_MAX) return 1;
    }}
}}
"""
    with tempfile.TemporaryDirectory(prefix="polly-") as directory:
        src = Path(directory) / "find.c"
        exe = Path(directory) / "find"
        src.write_text(source)
        subprocess.run(["cc", "-O3", "-march=native", "-o", exe, src], check=True)
        result = subprocess.run([exe], check=True, capture_output=True, text=True)
        return int(result.stdout.strip())


def solve_once(host=None, port=None):
    tube = Tube(host, port)
    try:
        banner = tube.recvuntil(b"which seed modifier would you like to use?\n")
        match = re.search(
            rb"encrypted flag is ([0-9a-fA-F]+), the nonce is ([0-9a-fA-F]+)",
            banner,
        )
        if not match:
            raise RuntimeError(f"could not parse banner: {banner!r}")
        flag_ct = bytes.fromhex(match.group(1).decode())
        flag_nonce = bytes.fromhex(match.group(2).decode())
        base_nonce, target = flag_nonce[:9], int.from_bytes(flag_nonce[9:], "big")
        shifts, num = get_parameters(base_nonce)
        jumps = build_jumps(shifts, num)

        print(f"[+] flag ciphertext: {flag_ct.hex()}")
        print(f"[+] target nonce:    {flag_nonce.hex()}")
        print(f"[+] shifts={shifts}, branch={num}")
        queries = choose_queries(jumps, flag_nonce)
        print(f"[+] seed is observable using {len(queries)} queries")
        seed = recover_seed(tube, queries)
        print(f"[+] recovered seed:  {seed:#018x}")

        x = find_collision(seed, target, shifts, num)
        print(f"[+] matching x:      {x} ({x:#x})")

        known = b"A" * len(flag_ct)
        leak, known_ct = query_nonce_byte(tube, x, known)
        assert leak == (target & 0xff)
        flag = bytes(a ^ b ^ c for a, b, c in zip(flag_ct, known_ct, known))
        print(f"[+] flag: {flag.decode(errors='replace')}")
        return flag
    finally:
        tube.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", nargs="?")
    parser.add_argument("port", nargs="?", type=int)
    args = parser.parse_args()
    if (args.host is None) != (args.port is None):
        parser.error("specify both HOST and PORT, or neither for local mode")

    if args.host is not None:
        solve_once(args.host, args.port)
        return

    # The distributed code documents that about one fifth of randomly generated
    # instances are unobservable.  In local mode, restart those instances.
    for attempt in range(1, 20):
        try:
            solve_once()
            return
        except RuntimeError as exc:
            if "not seed-observable" not in str(exc):
                raise
            print(f"[-] local attempt {attempt}: {exc}; restarting")
    raise RuntimeError("failed to obtain an observable local instance")


if __name__ == "__main__":
    main()
