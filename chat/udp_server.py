#!/usr/bin/env python3
"""
UDP backup server for CLI-Chat

Packet format: see proto.py — 1-byte TAG + 2-byte LEN + BODY
TAG b'U': UDP data
BODY    : bytes (UTF-8 encoding is up to the sender)

• Ping packets (b"__ping__") are replied to directly
• All other messages are echoed back to the client
"""

from __future__ import annotations
import argparse
import socket
import threading
from typing import Tuple

from chat import proto  # chat/proto.py

PING = b"__ping__"
TAG_UDP = b"U"
BUF_SIZE = 65535


def handle_packet(sock: socket.socket, data: bytes, addr: Tuple[str, int]) -> None:
    """
    Decode incoming packet, process it, and send a response.
    """
    try:
        _, body, _ = proto.decode(data)        # Tag isn't needed here
    except ValueError:
        print(f"[WARN] malformed packet from {addr}")
        return

    if body == PING:
        sock.sendto(proto.encode(PING, tag=TAG_UDP), addr)
        return

    print(f"← {addr}: {body!r}")
    sock.sendto(proto.encode(body, tag=TAG_UDP), addr)   # Echo back


def main() -> None:
    ap = argparse.ArgumentParser(description="UDP echo server (backup channel)")
    ap.add_argument("--host", default="0.0.0.0", help="Bind address")
    ap.add_argument("--port", type=int, default=9001, help="UDP port")
    args = ap.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))
    print(f"[UDP-SERVER] listening on {args.host}:{args.port}")

    while True:
        data, addr = sock.recvfrom(BUF_SIZE)
        threading.Thread(target=handle_packet,
                         args=(sock, data, addr),
                         daemon=True).start()


if __name__ == "__main__":
    main()
