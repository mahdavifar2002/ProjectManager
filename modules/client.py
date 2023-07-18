import socket


def receive_broadcast():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 5005))

    packet = sock.recvfrom(1024)
    message = packet[0].decode("ascii")

    return message


if __name__ == "__main__":
    receive_broadcast()
