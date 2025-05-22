#!/usr/bin/env python3
"""
tcp_server.py
~~~~~~~~~~~~~
Simple multithreaded TCP echo server for the CLI-Chat project.

Packet format  : see proto.py  ->  1-byte TAG | 2-byte LEN | BODY
TAG values     : b'T' (TCP data)  –  you can extend later if needed
Special body   : b"__ping__"      –  replied immediately for health-checks

The server accepts multiple concurrent clients, runs one thread per client,
and echoes every non-ping message back to the sender (for demo purposes).

If you want group chat, replace the `echo_back()` call with a broadcast loop.
"""

from __future__ import annotations

import argparse
import socket
import threading
from typing import Tuple

from chat import proto  # chat/proto.py

# --------------------------------------------------------------------------- #
PING_BODY = b"__ping__"
TAG_TCP = b"T"
BUFFER = 1 << 14  # 16 KiB

# --------------------------------------------------------------------------- #
def echo_back(sock: socket.socket, payload: bytes) -> None:
    """Send `payload` back to the connected TCP socket, framed for TCP."""
    try:
        sock.sendall(proto.encode(payload, tag=TAG_TCP))
    except OSError:
        # Broken pipe or other I/O error – the handler thread will exit soon
        pass


def client_handler(sock: socket.socket, addr: Tuple[str, int]) -> None:
    """Serve a single client until it disconnects."""
    print(f"[TCP-SERVER] New client {addr}")

    try:
        # Loop until the client closes the connection
        while True:
            try:
                tag, body = proto.recv_packet_tcp(sock)
            except ConnectionError:
                break  # socket closed
            except ValueError:
                # Malformed packet – skip or optionally close connection
                continue

            # Health-check ping
            if body == PING_BODY:
                echo_back(sock, PING_BODY)
                continue

            # Normal chat payload – here we simply echo
            print(f"[TCP-SERVER] {addr} -> {body!r}")
            echo_back(sock, body)

    finally:
        print(f"[TCP-SERVER] Client {addr} disconnected")
        try:
            sock.close()
        except Exception:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI-Chat TCP echo server")
    parser.add_argument("--host", default="0.0.0.0", help="bind address")
    parser.add_argument("--port", type=int, default=9000, help="TCP port")
    args = parser.parse_args()

    # Create, bind, and listen
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_sock.bind((args.host, args.port))
    serv_sock.listen()

    print(f"[TCP-SERVER] Listening on {args.host}:{args.port} (Ctrl-C to quit)")

    try:
        while True:
            client_sock, client_addr = serv_sock.accept()
            t = threading.Thread(
                target=client_handler, args=(client_sock, client_addr), daemon=True
            )
            t.start()
    except KeyboardInterrupt:
        print("\n[TCP-SERVER] Shutting down…")
    finally:
        serv_sock.close()


if __name__ == "__main__":
    main()
