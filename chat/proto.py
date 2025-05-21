"""
proto.py
--------
Common packet format ⇒ 1-byte TAG + 2-byte LEN + LEN-byte BODY

TAG  : b'T' = TCP, b'U' = UDP  (expandable to b'F' = file, b'C' = command, etc.)
LEN  : 0 to 65535, network-byte-order (big-endian)
BODY : bytes (UTF-8 encoding is up to the caller)
"""

from __future__ import annotations
import struct
from typing import Tuple

_HEADER_FMT = "!BH"  # 1 byte + 2 bytes → big-endian unsigned char, unsigned short
_HEADER_SIZE = struct.calcsize(_HEADER_FMT)  # = 3 bytes


def encode(body: bytes | str, tag: bytes = b"T") -> bytes:
    """
    Serialize the payload with TAG and LEN header.

    Parameters
    ----------
    body : bytes | str
        The data to send. If a str is provided, it will be UTF-8 encoded.
    tag : bytes, optional
        A 1-byte field indicating source/type. Defaults to b'T'.

    Returns
    -------
    bytes
        The complete serialized packet (header + body).
    """
    if isinstance(body, str):
        body = body.encode('utf-8')
    if not isinstance(body, (bytes, bytearray)):
        raise TypeError("body must be bytes, bytearray, or str")

    if len(tag) != 1:
        raise ValueError("tag must be exactly 1 byte")

    if len(body) > 0xFFFF:
        raise ValueError("body length exceeds 65535 bytes")

    header = struct.pack(_HEADER_FMT, tag[0], len(body))
    return header + body



def decode(buffer: bytes | bytearray) -> Tuple[bytes, bytes, bytes]:
    """
    Extract the first packet from a buffer, returning (tag, body, rest).

    Parameters
    ----------
    buffer : bytes | bytearray
        The receive buffer (from a TCP stream or UDP datagram).

    Returns
    -------
    Tuple[tag, body, rest]
        tag  : bytes(1)
        body : bytes
        rest : bytes — the remainder of the buffer after the packet

    Raises
    ------
    ValueError
        If the header is incomplete (< 3 bytes) or the buffer is shorter than LEN.
    """
    if len(buffer) < _HEADER_SIZE:
        raise ValueError("incomplete header")

    tag_byte, body_len = struct.unpack(_HEADER_FMT, buffer[:_HEADER_SIZE])
    total_len = _HEADER_SIZE + body_len

    if len(buffer) < total_len:
        raise ValueError("incomplete body")

    tag = bytes([tag_byte])
    body = buffer[_HEADER_SIZE:total_len]
    rest = buffer[total_len:]
    return tag, body, rest


# ---------- TCP stream-specific helpers ---------- #

def recv_exact(sock, n: int) -> bytes:
    """
    Block until exactly n bytes have been received from a TCP socket.

    Parameters
    ----------
    sock : socket.socket
        The connected TCP socket.
    n : int
        Number of bytes to receive.

    Returns
    -------
    bytes
        The received data of length n.

    Raises
    ------
    ConnectionError
        If the socket closes before n bytes are received.
    """
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("socket closed before receiving expected bytes")
        data.extend(chunk)
    return bytes(data)


def recv_packet_tcp(sock) -> Tuple[bytes, bytes]:
    """
    Receive exactly one packet (tag, body) from a TCP socket.

    Parameters
    ----------
    sock : socket.socket
        The connected TCP socket.

    Returns
    -------
    tag : bytes(1)
    body : bytes
    """
    header = recv_exact(sock, _HEADER_SIZE)
    tag_byte, body_len = struct.unpack(_HEADER_FMT, header)
    body = recv_exact(sock, body_len)
    return bytes([tag_byte]), body
