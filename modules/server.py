import socket
import threading
from time import sleep

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", 0))


def send_broadcast(message: str):
    sock.sendto(message.encode("ascii"), ("255.255.255.255", 50050))


def tcp_client_handler(conn, addr):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)


def tcp_echo_server(share_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((share_name, 50051))
        s.listen()
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=tcp_client_handler, args=(conn, addr))
            thread.daemon = True
            thread.start()


def start_tcp_server(share_name):
    thread = threading.Thread(target=tcp_echo_server, args=(share_name, ))
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    while True:
        msg = "Hello, world!"
        send_broadcast(msg)
        sleep(2)
