#!/usr/bin/env python3
"""
Interactive UDP client for CLI-Chat

• Reads stdin, wraps input in a proto packet (tag=b'U'), and sends via UDP
• Receives UDP datagrams, decodes via proto.decode, and prints messages
"""

from __future__ import annotations
import argparse
import select
import socket
import sys

import proto  # chat/proto.py

TAG_UDP = b"U"
PING = b"__ping__"
BUF_SIZE = 65535
SOCK_TIMEOUT = 2.0  # seconds


def main() -> None:
    ap = argparse.ArgumentParser(description="UDP client for CLI-Chat")
    ap.add_argument("--host", required=True, help="Server address")
    ap.add_argument("--port", type=int, default=9001, help="Server UDP port")
    args = ap.parse_args()

    server_addr = (args.host, args.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(SOCK_TIMEOUT)

    print(f"[UDP-CLIENT] chatting with {args.host}:{args.port}  (Ctrl-D/Ctrl-C to quit)")

    try:
        while True:
            # Prompt user input or wait for socket data
            sys.stdout.write("→ ")
            sys.stdout.flush()

            # Use select to handle stdin and socket asynchronously
            rlist, _, _ = select.select([sys.stdin, sock], [], [])

            # 1) User input available
            if sys.stdin in rlist:
                line = sys.stdin.readline()
                if not line:  # Ctrl-D
                    break
                # Encode input line into a UDP proto packet
                packet = proto.encode(line.rstrip("\n"), tag=TAG_UDP)
                sock.sendto(packet, server_addr)

            # 2) Socket data available
            if sock in rlist:
                try:
                    data, _ = sock.recvfrom(BUF_SIZE)
                    _, body, _ = proto.decode(data)
                    if body == PING:  # ignore monitoring pings
                        continue
                    print(f"\n← {body.decode(errors='replace')}")
                except (socket.timeout, ValueError):
                    continue

    except KeyboardInterrupt:
        pass
    finally:
        print("\n[UDP-CLIENT] bye 👋")


if __name__ == "__main__":
    main()
