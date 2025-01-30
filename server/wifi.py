import socket
import time

def is_connected_to_internet():
    try:
        # Check if we can resolve a hostname (Google's public DNS server)
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

while True:
    time.sleep(1)
    print(is_connected_to_internet())