"""
chat
====

A minimal package initializer for the CLI-Chat project.
Exposes the most useful sub-modules and a version string.
"""

from importlib.metadata import version, PackageNotFoundError

__all__ = [
    "tcp_client",
    "tcp_server",
    "udp_client",
    "udp_server",
    "link_monitor",
    "proto",
]

try:
    __version__ = version("chat") # Get version of 'chat' package
except PackageNotFoundError:
    __version__ = "0.3.0" # Fallback if not installed