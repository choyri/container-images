"""Test 3proxy against local endpoints without starting or registering WARP."""

import http.client
import http.server
import socket
import socketserver
import struct
import sys
import threading
import time

PAYLOAD = b"warp-proxy-smoke-test"
proxy = sys.argv[1]


def read_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        assert chunk, "Unexpected proxy EOF"
        data += chunk
    return data


class HTTP(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(PAYLOAD)

    def log_message(self, *args):
        pass


class TCP(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(5)
        self.request.sendall(read_exact(self.request, len(PAYLOAD)))


class UDP(socketserver.BaseRequestHandler):
    def handle(self):
        data, sock = self.request
        sock.sendto(data, self.client_address)


for port in (3128, 1080):
    deadline = time.monotonic() + 10
    while True:
        try:
            with socket.create_connection((proxy, port), timeout=1) as probe:
                client_ip = probe.getsockname()[0]
            break
        except OSError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.2)

servers = [
    http.server.ThreadingHTTPServer(("0.0.0.0", 0), HTTP),
    socketserver.ThreadingTCPServer(("0.0.0.0", 0), TCP),
    socketserver.ThreadingUDPServer(("0.0.0.0", 0), UDP),
]
for server in servers:
    threading.Thread(target=server.serve_forever, daemon=True).start()
http_port, tcp_port, udp_port = [server.server_address[1] for server in servers]


def socks():
    sock = socket.create_connection((proxy, 1080), timeout=5)
    sock.sendall(bytes.fromhex("050100"))
    assert read_exact(sock, 2) == bytes.fromhex("0500")
    return sock


connection = http.client.HTTPConnection(proxy, 3128, timeout=5)
connection.request("GET", f"http://{client_ip}:{http_port}/")
response = connection.getresponse()
assert response.status == 200 and response.read() == PAYLOAD
connection.close()
print("PASS HTTP forwarding", flush=True)

with socket.create_connection((proxy, 3128), timeout=5) as sock:
    target = f"{client_ip}:{tcp_port}"
    sock.sendall(f"CONNECT {target} HTTP/1.1\r\nHost: {target}\r\n\r\n".encode())
    header = b""
    while not header.endswith(b"\r\n\r\n"):
        header += read_exact(sock, 1)
        assert len(header) <= 65536, "Oversized CONNECT response"
    assert b" 200 " in header.split(b"\r\n")[0], header
    sock.sendall(PAYLOAD)
    assert read_exact(sock, len(PAYLOAD)) == PAYLOAD
print("PASS HTTP CONNECT", flush=True)

with socks() as sock:
    sock.sendall(
        bytes.fromhex("05010001")
        + socket.inet_aton(client_ip)
        + struct.pack("!H", tcp_port)
    )
    assert read_exact(sock, 10)[:4] == bytes.fromhex("05000001")
    sock.sendall(PAYLOAD)
    assert read_exact(sock, len(PAYLOAD)) == PAYLOAD
print("PASS SOCKS5 TCP", flush=True)

with socks() as control, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp:
    udp.bind(("0.0.0.0", 0))
    udp.settimeout(5)
    control.sendall(
        bytes.fromhex("0503000100000000") + struct.pack("!H", udp.getsockname()[1])
    )
    reply = read_exact(control, 10)
    assert reply[:4] == bytes.fromhex("05000001"), reply
    relay = socket.inet_ntoa(reply[4:8]), struct.unpack("!H", reply[8:])[0]
    packet = (
        bytes.fromhex("00000001")
        + socket.inet_aton(client_ip)
        + struct.pack("!H", udp_port)
        + PAYLOAD
    )
    udp.sendto(packet, relay)
    response, _ = udp.recvfrom(4096)
    assert response[:4] == bytes.fromhex("00000001") and response[10:] == PAYLOAD
print("PASS SOCKS5 UDP ASSOCIATE", flush=True)
