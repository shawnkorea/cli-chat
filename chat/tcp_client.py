#!/usr/bin/env python3
"""
tcp_client.py
~~~~~~~~~~~~~
Main interactive client for CLI-Chat.

• Primary transport is TCP; if disconnected, LinkMonitor will automatically switch to UDP
• Uses common packet format from proto.py (1-byte TAG + 2-byte LEN + BODY)
• Chat between stdin and server; exit on Ctrl-D or Ctrl-C
"""

from __future__ import annotations

import argparse
import select
import socket
import sys
from typing import Tuple

from chat import proto  # chat/proto.py
from .link_monitor import LinkMonitor

TAG_TCP = b"T"
TAG_UDP = b"U"
PING = b"__ping__"
BUF_SIZE = 65535
SOCK_TIMEOUT = 2.0                 # UDP receive timeout (seconds)


def create_tcp_socket(addr: Tuple[str, int]) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.setblocking(True)
    return sock


def create_udp_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(SOCK_TIMEOUT)
    return sock


def main() -> None:
    # ----- argparse configuration -----
    ap = argparse.ArgumentParser(description="CLI-Chat client with TCP→UDP fail-over")
    ap.add_argument("--host", required=True, help="Server address")
    ap.add_argument("--tcp-port", type=int, default=9000, help="Server TCP port")
    ap.add_argument("--udp-port", type=int, default=9001, help="Server UDP port")
    args = ap.parse_args()

    server_tcp = (args.host, args.tcp_port)
    server_udp = (args.host, args.udp_port)

    # ----- socket setup -----
    tcp_sock = create_tcp_socket(server_tcp)
    udp_sock = create_udp_socket()

    # ----- link monitor start -----
    def on_switch(ch: str) -> None:
        print(f"\n[MONITOR] ⇢ Active channel switched to **{ch.upper()}**")

    monitor = LinkMonitor(
        tcp_sock,
        udp_sock,
        server_udp,
        on_switch_cb=on_switch,
    )
    monitor.start()

    print(
        f"[CLIENT] connected to {args.host}  "
        f"(TCP:{args.tcp_port} / UDP:{args.udp_port}) — Ctrl-D/Ctrl-C to quit"
    )

    tcp_buffer = bytearray()

    try:
        while True:
            sys.stdout.write("→ ")
            sys.stdout.flush()

            # select: stdin + whichever channel is active
            rlist = [sys.stdin]
            if monitor.active == "tcp":
                rlist.append(tcp_sock)
            else:
                rlist.append(udp_sock)

            readable, _, _ = select.select(rlist, [], [])

            # ----- 1) User input -----
            if sys.stdin in readable:
                line = sys.stdin.readline()
                if not line:                 # EOF (Ctrl-D)
                    break
                body = line.rstrip("\n").encode()
                tag = TAG_TCP if monitor.active == "tcp" else TAG_UDP
                packet = proto.encode(body, tag=tag)
                try:
                    if monitor.active == "tcp":
                        tcp_sock.sendall(packet)
                    else:
                        udp_sock.sendto(packet, server_udp)
                except (BrokenPipeError, OSError):
                    # Sending failed; monitor will switch channels
                    pass

            # ----- 2) Server response -----
            if monitor.active == "tcp" and tcp_sock in readable:
                try:
                    chunk = tcp_sock.recv(BUF_SIZE)
                    if not chunk:
                        raise ConnectionError("TCP closed by server")
                    tcp_buffer.extend(chunk)
                    while True:
                        try:
                            tag, body, rest = proto.decode(tcp_buffer)
                        except ValueError:
                            break        # incomplete packet
                        tcp_buffer[:] = rest
                        if body != PING:
                            print(f"\n← {body.decode(errors='replace')}")
                except Exception:
                    # Monitor will handle switching
                    pass

            if monitor.active == "udp" and udp_sock in readable:
                try:
                    data, _ = udp_sock.recvfrom(BUF_SIZE)
                    _, body, _ = proto.decode(data)
                    if body != PING:
                        print(f"\n← {body.decode(errors='replace')}")
                except Exception:
                    pass

    except KeyboardInterrupt:
        pass
    finally:
        print("\n[CLIENT] shutting down…")
        monitor.stop()
        monitor.join()
        tcp_sock.close()
        udp_sock.close()


if __name__ == "__main__":
    main()
