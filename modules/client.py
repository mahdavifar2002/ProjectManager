import socket
import threading


def receive_broadcast():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 50050))

    packet = sock.recvfrom(1024)
    message = packet[0].decode("ascii")

    return message


def check_share_lazy(share_name):
    try:
        socket.getaddrinfo(share_name, 445, family=socket.AF_INET, proto=socket.IPPROTO_TCP)
        return True
    except socket.gaierror:
        return False


def check_share(share_name):
    t = threading.Thread(target=check_share_lazy, args=(share_name,))
    t.daemon = True
    t.start()
    timeout_seconds = 0.2  # Replace with your desired timeout value in seconds
    t.join(timeout_seconds)  # Set the timeout for the thread's runtime

    if t.is_alive():
        return False
    else:
        return True


def check_online_lazy(share_name):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.2)
    result = sock.connect_ex((share_name, 50051))
    sock.close()
    if result == 0:
        return True
    else:
        return False


def check_online(share_name):
    t = threading.Thread(target=check_online_lazy, args=(share_name,))
    t.daemon = True
    t.start()
    timeout_seconds = 0.2  # Replace with your desired timeout value in seconds
    t.join(timeout_seconds)  # Set the timeout for the thread's runtime

    if t.is_alive():
        return False
    else:
        return True


if __name__ == "__main__":
    receive_broadcast()
