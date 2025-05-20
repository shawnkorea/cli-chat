import socket, threading

HOST = "127.0.0.1"
PORT = 5000

def run_server(host: str = HOST, port: int = PORT) -> None:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen()
    print(f"💬 Listening on {host}:{port} ...")
    
    clients: dict[socket.socket, str] = {}

    def broadcast(msg: str, sender: socket.socket | None = None) -> None:
        for conn in list(clients):
            if conn is sender:
                continue
            try:
                conn.sendall(msg.encode())
            except (BrokenPipeError, ConnectionResetError):
                clients.pop(conn, None)

    def handle_client(conn: socket.socket) -> None:
        try:
            nickname = conn.recv(1024).decode().strip() or "Anon"
            clients[conn] = nickname
            broadcast(f"👋 {nickname} has joined.")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                broadcast(f"{nickname}: {data.decode().strip()}", conn)
        except ConnectionResetError:
            pass
        finally:
            left = clients.pop(conn, nickname)
            broadcast(f"❌ {left} left.")
            conn.close()

    while True:
        conn, _ = server_sock.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    run_server()
