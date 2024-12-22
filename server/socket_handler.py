import socket

def configure_socket_UDP(litsen = False, broadcast = False):
    if broadcast:
        # Create a UDP socket
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        # Enable broadcasting mode
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        return broadcast_socket
    elif litsen:
        # Create a UDP socket
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set the socket to broadcast and enable reusing addresses
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind socket to address and port
        listen_socket.bind(('', BROADCAST_PORT))
        return listen_socket

def sendmessagethroughUDP(UDP_socket, message, client_address):
    UDP_socket.sendto(client_address, message)

def close_socket(broadcast_socket):
    #close the socket
    broadcast_socket.close()

def configuresocketTCP():
    # Create a TCP socket
    TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    return TCP_socket

def connecttoServer(client_socket,host,port):
    #connecting to the server
    client_socket.connect((host,port))

def sendMessagethroughTCPSocket(client_socket, message):
    #sending message to the server
    client_socket.send(message.encode())

def recvMessagefromTCPSocket(socket):
    #sending message to the server
    return socket.recv(1024).decode()

def bindtoaAddress(TCP_socket,host,port):
    # Bind the socket to the host and port
    TCP_socket.bind((host, port))

def litsentoaSocket(TCP_socket):
    #litsening to socket
    TCP_socket.litsen(1)

def accepttheConnection(TCP_socket):
    #accepting the connection
    client_socket, client_address = TCP_socket.accept()
    return client_socket

def tcpsocketforServer():
    server_scoket = configuresocketTCP()
    bindtoaAddress(server_scoket, client_address)
    litsentoaSocket(server_scoket)
    client_socket, client_address = accepttheConnection(server_scoket)
    return server_scoket, client_socket, client_address
