import socket
from time import time

result = (False, 0)


def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Check the Internet connectivity.

    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    global result
    if result[1] - time() < 30:
        return result[0]

    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        ret = True
    except socket.error:
        ret = False

    result = (time(), ret)
    return ret
