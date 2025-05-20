#!/usr/bin/env python3
"""
cli-chat: Simple terminal chat that can switch between TCP and UDP.

Usage examples:
    python chat.py --mode server
    python chat.py --mode client --host 192.168.0.10
"""

import argparse
import sys
from . import run_server, run_client, HOST, PORT

def parse_args():
    p = argparse.ArgumentParser(
        description="CLI chat over TCP with UDP fallback"
        )
    p.add_argument(
        "--mode", choices=["server", "client"], 
        required=True,
        help="Run as a server or client"
        )
    p.add_argument(
        "--host", default=HOST,
        help="Server host to (bind/connect)"
        )
    p.add_argument(
        "--port", type=int, default=PORT,
        help="TCP/UDP port"
        )
    p.add_argument(
        "--name", 
        help="Nickname (required in client mode)"
        )
    return p.parse_args()

def main():
    args = parse_args()
    
    if args.mode == "server":
        print(f"🚀 Starting SERVER on {args.host}:{args.port}")
        run_server(args.host, args.port)
    else:
        if not args.name:
            print("‼️ -- name required in client mode", file=sys.stderr)
            sys.exit(1)
        print(f"🤝 connecting to {args.host}:{args.port} as {args.name}")
        run_client(args.host, args.port, args.name)

if __name__ == "__main__":
    main()