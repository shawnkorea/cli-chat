#!/usr/bin/env python3
"""
link_monitor.py
~~~~~~~~~~~~~~
Periodically ping both TCP and UDP channels to maintain the alive one as **active**.

Behavior:
    1. Send a PING packet over the currently active channel (default: TCP)
    2. If no response arrives within timeout, increment fail_count
    3. If fail_count ≥ fail_threshold, switch to the other channel
    4. On successful response, reset fail_count and continue

External API:
    - self.active       : "tcp" | "udp" (currently active channel)
    - self.stop()       : Stop the monitor thread
    - on_switch_cb      : Optional callback invoked on channel switch

Usage example:
-------
>>> monitor = LinkMonitor(tcp_sock, udp_sock, udp_addr,
...                       on_switch_cb=lambda ch: print("Switched to", ch))
>>> monitor.start()
>>> # ... chat logic using monitor.active ...
>>> monitor.stop(); monitor.join()
"""

from __future__ import annotations
import threading
import time
import socket
from typing import Callable, Optional, Tuple

import proto  # chat/proto.py

PING = b"__ping__"
TAG_TCP = b"T"
TAG_UDP = b"U"


class LinkMonitor(threading.Thread):
    """
    Monitors and switches between TCP and UDP channels based on ping responses.

    Parameters
    ----------
    tcp_sock : socket.socket
        A connected TCP socket (blocking or non-blocking).
    udp_sock : socket.socket
        A bound/connected UDP socket.
    udp_addr : Tuple[str, int]
        The server address for UDP.
    interval : float, default=3.0
        Ping interval in seconds.
    timeout : float, default=1.0
        Response wait timeout in seconds.
    fail_threshold : int, default=3
        Consecutive failures before switching channel.
    on_switch_cb : Callable[[str], None], optional
        Callback invoked with new channel name when switching.
    """

    def __init__(
        self,
        tcp_sock: socket.socket,
        udp_sock: socket.socket,
        udp_addr: Tuple[str, int],
        *,
        interval: float = 3.0,
        timeout: float = 1.0,
        fail_threshold: int = 3,
        on_switch_cb: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(daemon=True)
        self.tcp_sock = tcp_sock
        self.udp_sock = udp_sock
        self.udp_addr = udp_addr

        self.interval = interval
        self.timeout = timeout
        self.fail_threshold = fail_threshold
        self.on_switch_cb = on_switch_cb

        self.active: str = "tcp"   # currently active channel
        self._running = threading.Event()
        self._running.set()

    # ---------- Internal helpers ---------- #
    def _send_ping_tcp(self) -> None:
        pkt = proto.encode(PING, tag=TAG_TCP)
        self.tcp_sock.sendall(pkt)
        self.tcp_sock.settimeout(self.timeout)
        proto.recv_packet_tcp(self.tcp_sock)  # receive & verify reply

    def _send_ping_udp(self) -> None:
        pkt = proto.encode(PING, tag=TAG_UDP)
        self.udp_sock.sendto(pkt, self.udp_addr)
        self.udp_sock.settimeout(self.timeout)
        data, _ = self.udp_sock.recvfrom(65535)
        _, body, _ = proto.decode(data)
        if body != PING:
            raise ValueError("unexpected UDP pong body")

    # ---------- Thread main ---------- #
    def run(self) -> None:
        fail_cnt = 0
        while self._running.is_set():
            start = time.perf_counter()
            try:
                if self.active == "tcp":
                    self._send_ping_tcp()
                else:
                    self._send_ping_udp()
                # successful response
                fail_cnt = 0
            except Exception:
                fail_cnt += 1
                if fail_cnt >= self.fail_threshold:
                    # switch channel
                    self.active = "udp" if self.active == "tcp" else "tcp"
                    fail_cnt = 0
                    if self.on_switch_cb:
                        self.on_switch_cb(self.active)
            # sleep remaining interval
            elapsed = time.perf_counter() - start
            if elapsed < self.interval:
                time.sleep(self.interval - elapsed)

    # ---------- External API ---------- #
    def stop(self) -> None:
        """
        Signal the monitor thread to stop and wake any pending recv.
        """
        self._running.clear()
        # send dummy data to break out of a blocking recv
        try:
            if self.active == "tcp":
                self.tcp_sock.shutdown(socket.SHUT_RDWR)
            else:
                self.udp_sock.sendto(b"", self.udp_addr)
        except Exception:
            pass
