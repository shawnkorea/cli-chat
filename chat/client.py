import socket, sys, threading, os

def run_client(host: str, port: int, name: str) -> None:
    """Connect to a chat server and handle send/receive loops."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.sendall(name.encode())
    except Exception as e:
        print(f"❌ Connection error: {e}", file=sys.stderr)
        sys.exit(1)

    def listen() -> None:
        while True:
            try:
                data = sock.recv(1024)
            except ConnectionResetError:
                data = b""
            if not data:
                print("🔌 Disconnected")
                # Terminate the entire process, not just this thread
                os._exit(0)
            # Re-draw the incoming message + prompt immediately
            print("\r" + data.decode().strip() + "\n> ", end="", flush=True)

    threading.Thread(target=listen, daemon=True).start()

    try:
        while True:
            msg = input("> ").strip()
            if not msg:
                continue
            try:
                sock.sendall(msg.encode())
            except Exception:
                print("⚠️ Failed to send message", file=sys.stderr)
    except (KeyboardInterrupt, EOFError):
        # Ctrl-C or Ctrl-D to quit
        pass
    finally:
        sock.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CLI Chat Client")
    parser.add_argument("-n", "--name", required=True, help="Your chat nickname")
    parser.add_argument("-H", "--host", default="127.0.0.1", help="Server host")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Server port")
    args = parser.parse_args()
    run_client(args.host, args.port, args.name)