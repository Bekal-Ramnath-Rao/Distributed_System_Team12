import socket 
import time

class server:

    def __init__(self,leader,litsen_socket,broadcast_socket):
        self.leader = leader
        self.litsen_socket = litsen_socket
        self.broadcast_socket = broadcast_socket
    
    def configure_socket(litsen = False, broadcast = False):
        if broadcast:
            # Create a UDP socket
            server.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
            # Enable broadcasting mode
            server.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            return server.broadcast_socket
        elif litsen:
            # Create a UDP socket
            server.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Set the socket to broadcast and enable reusing addresses
            server.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            server.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind socket to address and port
            server.listen_socket.bind(('', BROADCAST_PORT))
            return server.listen_socket

    def close_socket(broadcast_socket):
        broadcast_socket.close()

    def broadcast_tobecomeaServer(ip, port, broadcast_message):
        broadcast_socket = server.configure_socket(broadcast = True)
        broadcast_socket.sendto(str.encode(broadcast_message), (ip, port))
        server.close_socket(broadcast_socket)


    def check_firstServer():
        # Listening port
        BROADCAST_PORT = 5973
        Data_Received = False
        # Local host information
        MY_HOST = socket.gethostname()
        MY_IP = socket.gethostbyname(MY_HOST)

        print("Listening to message from Leader server to join the group")
        while time.sleep(10):
            server.listen_socket = server.configure_socket(litsen = True)
            data, addr = server.listen_socket.recvfrom(1024)
            if data:
                print("Received broadcast message:", data.decode())
                break
            else:
                Data_Received = True
        return Data_Received

    def check_joinThegroup():
        if not server.leader:
            data, addr = server.listen_socket.recvfrom(1024)
            if MY_IP in data:
                return True
            else:
                return False

    def get_groupView():
        ''
    
    def setleader():
        server.leader = True

if __name__ == '__main__':
    # Broadcast address and port
    BROADCAST_IP = "192.168.56.255"
    BROADCAST_PORT = 5001

    # Local host information
    MY_HOST = socket.gethostname()
    MY_IP = socket.gethostbyname(MY_HOST)

    # Send broadcast message
    message = 'I want to be server'
    server.broadcast_tobecomeaServer(BROADCAST_IP, BROADCAST_PORT, message)
    if server.check_firstServer():
        server.setleader()
    else:
        if(server.check_joinThegroup()):
            server.get_groupView()
    
    if(server.leader):
        manage_requestfromClient()
        do_Replication()
        maintain_heartbeatMechanism()
