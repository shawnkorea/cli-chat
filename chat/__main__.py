#!/usr/bin/env python3
"""
python -m chat
==============

A thin convenience launcher that delegates to one of four
concrete entry-points:

    • tcp-client   → chat.tcp_client.main()
    • tcp-server   → chat.tcp_server.main()
    • udp-client   → chat.udp_client.main()
    • udp-server   → chat.udp_server.main()

Example
-------
$ python -m chat tcp-client --host 127.0.0.1 --tcp-port 9000 --udp-port 9001
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from textwrap import dedent

# --------------------------------------------------------------------------- #
COMMAND_MAP = {
    "tcp-client": "tcp_client",
    "tcp-server": "tcp_server",
    "udp-client": "udp_client",
    "udp-server": "udp_server",
}


def _usage(exit_code: int = 0) -> None:
    executable = Path(sys.argv[0]).name
    print(
        dedent(
            f"""
            Usage:
              {executable} <command> [options]

            Commands:
              tcp-client   Run the interactive TCP/UDP fail-over client
              tcp-server   Start the multithreaded TCP echo server
              udp-client   Simple standalone UDP echo client
              udp-server   Simple UDP echo server

            Try:
              {executable} tcp-client --help
            """
        ).strip()
    )
    sys.exit(exit_code)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        _usage(exit_code=0)

    cmd, *rest = sys.argv[1:]
    module_name = COMMAND_MAP.get(cmd)
    if module_name is None:
        print(f"[chat] Unknown command: {cmd!r}\n")
        _usage(exit_code=1)

    # Re-shape sys.argv so the delegated module sees the expected argument list
    sys.argv = [cmd] + rest

    # Dynamically import and call its main()
    module = import_module(f".{module_name}", package=__package__)
    if not hasattr(module, "main"):
        raise RuntimeError(f"Module '{module_name}' has no callable main()")
    module.main()


if __name__ == "__main__":
    main()
