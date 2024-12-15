import socket 
import time
import managing_request
import socket_handler

class server:

    def __init__(self,leader,litsen_socket,broadcast_socket):
        self.leader = leader
        self.litsen_socket = litsen_socket
        self.broadcast_socket = broadcast_socket
    
    def broadcast_tobecomeaServer(ip, port, broadcast_message):
        broadcast_socket = socket_handler.configure_socket_UDP(broadcast = True)
        broadcast_socket.sendto(str.encode(broadcast_message), (ip, port))
        socket_handler.close_socket(broadcast_socket)

    def check_firstServer():
        # Listening port
        BROADCAST_PORT = 5973
        Data_Received = False
        # Local host information
        MY_HOST = socket.gethostname()
        MY_IP = socket.gethostbyname(MY_HOST)

        print("Listening to message from Leader server to join the group")
        while time.sleep(10):
            server.listen_socket = socket_handler.configure_socket_UDP(litsen = True)
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
        managing_request.managingRequestfromClient.getRequestfromclient()
        do_Replication()
        maintain_heartbeatMechanism()
