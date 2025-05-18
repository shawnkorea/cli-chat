#!/usr/bin/env python3
"""
cli-chat: Simple terminal chat that can switch between TCP and UDP.

Usage examples:
    python chat.py --mode server
    python chat.py --mode client --host 192.168.0.10
"""

import argparse
import socket
import sys

def parse_args():
    p = argparse.ArgumentParser(description="CLI chat over TCP with UDP fallback")
    p.add_argument("--mode", choices=["server", "client"], required=True,
                   help="Run as a server or client")
    p.add_argument("--host", default="0.0.0.0",
                   help="Server host to bind/connect (default: %(default)s)")
    p.add_argument("--port", type=int, default=5000,
                   help="TCP/UDP port (default: %(default)s)")
    p.add_argument("--transport", choices=["tcp", "udp", "auto"],
                   default="auto", help="Preferred transport (default: auto)")
    return p.parse_args()

def main():
    args = parse_args()
    print(f"🚀 Starting in {args.mode.upper()} mode on {args.host}:{args.port} "
          f"({args.transport.upper()})")
    # TODO: tomorrow we'll drop in the real networking logic.
    sys.exit(0)

if __name__ == "__main__":
    main()
