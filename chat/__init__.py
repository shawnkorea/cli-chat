"""CLI Chat package - TCP/UDP command-line messenger."""

__version__ = "0.1.0"
HOST = "127.0.0.1"
PORT = 5000

from .server import run_server
from .client import run_client

__all__ = ["run_server", "run_client", "HOST", "PORT", "__version__"]
