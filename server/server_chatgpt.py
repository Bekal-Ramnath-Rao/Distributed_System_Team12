import socket
import threading
import time
from share_handler import share_handler
from managing_request import managingRequestfromClient
from managing_request import managingRequestfromClientEncoder
from election_handler import lcr_election_handler
import socket_handler
import ast
import json
import pickle
import ctypes

LEADER_HOST = None  # The leader's host address (dynamically updated)
LEADER_TCP_PORT = None  # The leader's TCP port (dynamically updated)
SERVER_UDP_PORT = 12345
SERVER_TCP_PORT = 12346
TIMEOUT = 3  # Timeout for leader election (in seconds)
is_server_group_updated = False
i_initiated_election = False
IS_LEADER = False
server_group = []  # List of (host, port) tuples for all servers in the group
neighbor_sockets = []  # List of active neighbor connections
clientobjectflag = False
COLLECTION_THREAD_IS = []

import threading
import time

# Shared data structure to store thread information
thread_info = []
info_lock = threading.Lock()  # To ensure thread-safe access
client_share = None

def setclientshareobject(client_share_object):
    global client_share
    client_share = client_share_object

def getclientshareobject():
    global client_share
    return client_share

def setclientsharehandlerobject(clientsharehandler_object):
    global clientsharehandler
    clientsharehandler = clientsharehandler_object

def getclientsharehandlerobject():
    global clientsharehandler
    return clientsharehandler

def setleaderstatus(status):
    global IS_LEADER
    IS_LEADER = status

def getleaderstatus():
    global IS_LEADER
    return IS_LEADER

def handle_client(conn, client_address,client_share = None):
    """Handle communication with a single client."""
    print(f"TCP connection established with {client_address}")
    try:
        while True:
            if getleaderstatus():
                client_message = conn.recv(1024).decode()
                if not client_message or client_message.lower() == "exit":
                    print(f"Client {client_address} requested to close the connection.")
                    break
                else:
                    # Process the request as the leader
                    filtered_string = list(client_message.split())
                        

                    if filtered_string[1] in ("b", "B"):
                        number_of_shares = int(filtered_string[3])
                        name_of_the_share = filtered_string[2]
                        transaction_result = client_share.executetheBuyrequest(
                            number_of_shares, name_of_the_share, filtered_string[0]
                        )
                        server_response = (
                            "Transaction successful"
                            if transaction_result
                            else "Transaction failed"
                        )
                        conn.send(server_response.encode())
                    elif filtered_string[1] in ("s", "S"):
                        number_of_shares = int(filtered_string[3])
                        name_of_the_share = filtered_string[2]
                        transaction_result = client_share.executetheSellrequest(
                            number_of_shares, name_of_the_share, filtered_string[0]
                        )
                        server_response = (
                            "Transaction successful"
                            if transaction_result
                            else "Transaction failed"
                        )
                        conn.send(server_response.encode())
                    elif filtered_string[1] in ("i", "I"):
                        Data = client_share.executetheInquiryrequest(filtered_string[0])
                        Data = str(Data)
                        conn.send(Data.encode())

            print(f"Received message from {client_address}: {client_message}")

    except Exception as e:
        print(f"Error with client {client_address}: {e}")
        conn.close()
        print(f"Connection closed with {client_address}.")


def tcp_server(tcp_port, is_leader, client_share):
    """Handle multiple clients via TCP."""

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("0.0.0.0", tcp_port))  # Bind to all interfaces
    tcp_socket.listen(5)  # Allow up to 5 clients to queue for connections
    print(f"Leader server is listening on TCP port {tcp_port}...")

    try:
        while True:
            if getleaderstatus():
                if getclientshareobject() is not None:
                    conn, client_address = tcp_socket.accept()
                    client_thread = threading.Thread(
                        target=handle_client, args=(conn, client_address, getclientshareobject())
                    )
                    client_thread.start()
                    print(f"Started thread for client {client_address}")


    except KeyboardInterrupt:
        print("Server is shutting down.")
        tcp_socket.close()
        print("TCP server closed.")


def udp_server(udp_port, tcp_port, is_leader_flag, lcr_obj=None):
    """Handle UDP communication for leader election, server group management, and client communication."""
    global LEADER_HOST, LEADER_TCP_PORT, server_group, is_server_group_updated

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind(("", udp_port))  # Listen on all interfaces

    if getleaderstatus():
        print(
            f"Leader server is waiting for broadcast messages on UDP port {udp_port}..."
        )
    else:
        print(
            f"Follower server is waiting for broadcast messages on UDP port {udp_port}..."
        )
    ##time.sleep(2)
    while True:
        try:
            message, client_address = udp_socket.recvfrom(4096)
            message = message.decode()
            print(f"Received message '{message}' from {client_address}")

            if getleaderstatus():
                # Leader responds to server broadcast messages
                if message.startswith("NEW_SERVER"):
                    # server_group.append(client_address)
                    received_uid = str(message.split()[2])
                    lcr_obj.create_IP_UID_mapping(client_address[0], received_uid)
                    server_group = update_ip_list(server_group, client_address, lcr_obj.IP_UID_mapping)
                    unicast_message = (
                        f"ACK_LEADER {tcp_port} SERVER_GROUP {server_group}"
                    )
                    udp_socket.sendto(unicast_message.encode(), client_address)
                    print(f"Added new server {client_address} to the group.")
                    print("current server group is ", server_group)
                # Handle client inquiries to identify the leader
                elif message == "WHO_IS_LEADER":
                    leader_info = f"LEADER {tcp_port}"
                    udp_socket.sendto(leader_info.encode(), client_address)
                    print(f"Sent leader information to client {client_address}.")
                elif message == "SEND_SERVER_GROUP":
                    server_group = update_ip_list(server_group, client_address, lcr_obj.IP_UID_mapping)
                    server_group_str = "UPDATED_SERVER_GROUP " + str(server_group)
                    print(
                        "server group before sending to all clients is ",
                        server_group_str,
                    )
                    print(client_address)
                    udp_socket.sendto(
                        server_group_str.encode(), ("192.168.0.255", 12345)
                    )
                    print(f"Sent server group to ALL clients")
                    is_server_group_updated = True
                    lcr_obj.election_done = False

            else:
                # Followers listen for leader acknowledgment or respond to client inquiries
                if message.startswith("ACK_LEADER"):
                    leader_port = int(message.split()[1])
                    LEADER_HOST, LEADER_TCP_PORT = client_address[0], leader_port
                    print(f"Leader found at {LEADER_HOST}:{LEADER_TCP_PORT}.")
                    udp_socket.sendto("SEND_SERVER_GROUP".encode(), client_address)
                elif message.startswith("UPDATED_SERVER_GROUP"):
                    server_group = ast.literal_eval(message[21:])
                    is_server_group_updated = True
                    print("updated server group from leader is", server_group)
                    # update the server group here

        except KeyboardInterrupt:
            print("Shutting down UDP server.")
            break

    udp_socket.close()
    print("UDP server closed.")


def update_ip_list(ip_list, new_tuple, IP_UID_mapping=None):
    # Create a dictionary to store the latest tuple for each unique IP address
    ip_dict = {ip: (ip, port, IP_UID_mapping[ip]) for ip, port in ip_list}

    # Update the dictionary with the new tuple
    ip_dict[new_tuple[0]] = new_tuple

    # Convert the dictionary values back to a list
    return list(ip_dict.values())


def get_machines_ip():
    udp_socket_for_ip_retrieval = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket_for_ip_retrieval.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket_for_ip_retrieval.connect(
        ("8.8.8.8", 80)
    )  # Google's public DNS server (doesn't send actual data)
    print("local IP is ", udp_socket_for_ip_retrieval.getsockname()[0])
    return udp_socket_for_ip_retrieval.getsockname()[0]


def leader_election(udp_port, broadcast_ip, lcr_obj=None):
    """Perform leader election by broadcasting and waiting for a response."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print("Broadcasting leader election message...")
    newserver_message = f"NEW_SERVER = {lcr_obj.uid}"
    udp_socket.sendto(newserver_message.encode(), (broadcast_ip, udp_port))

    udp_socket.settimeout(TIMEOUT)
    try:
        message, server_address = udp_socket.recvfrom(4096)
        if message.decode().startswith("ACK_LEADER"):
            leader_port = int(message.decode().split()[1])
            global LEADER_HOST, LEADER_TCP_PORT
            server_group = message.decode()[30:]
            LEADER_HOST, LEADER_TCP_PORT = server_address[0], leader_port
            print(f"Leader acknowledged at {LEADER_HOST}:{LEADER_TCP_PORT}.")
            return False, server_group  # This server is not the leader
    except socket.timeout:
        print("No leader found. Declaring self as leader.")
        return True, []  # This server becomes the leader
    finally:
        udp_socket.close()


def start_election(udp_port, broadcast_ip):
    """Start the election process by sending messages to neighbors."""
    global i_initiated_election
    # broadcast to server that election will be initiated and send the server group
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print("Asking server to broadcast server group...")
    udp_socket.sendto("SEND_SERVER_GROUP".encode(), (broadcast_ip, udp_port))
    i_initiated_election = True
    # use this when we do not receive a response of server_group from leader
    # this happens when the leader is not present
    # udp_socket.settimeout(TIMEOUT)
    udp_socket.close()


def server_reinitialise_UDPbuffer(udp_socket):
    udp_socket.close()
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind(("", 12347))  # Listen on all interfaces
    return udp_socket

def udp_server_managing_election(udp_socket, lcr_obj, is_leader, clientsharehandler = None, client_share = None, sharehandler = None):

    global is_server_group_updated, i_initiated_election, server_group, LEADER_HOST, LEADER_TCP_PORT
    print("inside election thread")
    FIRST_TIME = True
    latest_message = None
    while True:

        if is_server_group_updated:
            lcr_obj.group_view = server_group
            lcr_obj.form_members(server_group)
            lcr_obj.form_ring()
            lcr_obj.neighbour = lcr_obj.get_neighbour()[0]
            is_server_group_updated = False
            FIRST_TIME = False
            if i_initiated_election and not getleaderstatus():
                lcr_obj.initiate_election()
                i_initiated_election = False

        if not FIRST_TIME and not lcr_obj.election_done:
            try:
                while True:
                    data, addr = lcr_obj.udp_socket.recvfrom(1024)  # Buffer size of 1024 bytes
                    print(f"Received message: {data.decode()} from {addr}")
                    latest_message = data
            except BlockingIOError:
            # This exception occurs when the buffer is empty
                if latest_message is not None:
                    print("\nBuffer is empty. Processing the latest message:")
                    # print(f"Latest Message: {latest_message}")
                    # Process the latest message here
                    lcr_obj.process_received_message(latest_message)
                    latest_message = None  # Reset after processing

            # data, addr = lcr_obj.udp_socket.recvfrom(4096)  # Buffer size of 1024 bytes
            # print(
                # f"Received message from neighbour: {data.decode().strip()} from {addr}"
            # )
            # lcr_obj.process_received_message(data)

        elif not FIRST_TIME and lcr_obj.election_done:
            if lcr_obj.get_leader_status():
                if not getleaderstatus():
                    #data = lcr_obj.udp_socket.recvfrom(4096)
                    try:
                        while True:
                            received_data, addr = lcr_obj.udp_socket.recvfrom(1024)  # Buffer size of 1024 bytes
                            print(f"Received message: {received_data.decode()} from {addr}")
                            latest_message = received_data
                        
                    except BlockingIOError:
                        # This exception occurs when the buffer is empty
                        if latest_message is not None:
                            print("\nBuffer is empty. Processing the latest message:")
                            # print(f"Latest Message: {latest_message}")
                            # Process the latest message here
                            deserialized_object = latest_message.decode()
                            deserialized_object_list  = ast.literal_eval(deserialized_object)
                            list_of_dicts = [json.loads(item) for item in deserialized_object_list]
                            print("Received serialized object list from leader", list_of_dicts)
                            clientsharehandler = share_handler.clientshare_handler.from_dict(list_of_dicts[0])
                            sharehandler = share_handler.share_handler.from_dict(list_of_dicts[1])
                            # client_share = managingRequestfromClient.from_dict(list_of_dicts[2])
                            client_share = managingRequestfromClient(sharehandler, clientsharehandler, 'FOLLOWER')
                            setleaderstatus(True)
                            setclientshareobject(client_share) 
                            setclientsharehandlerobject(clientsharehandler)                    
                            FIRST_TIME = True
                            lcr_obj.election_done = False
                            lcr_obj.is_leader=True
                            FIRST_TIME = True
                            latest_message = None  # Reset after processing

            else:
                if getleaderstatus():
                    list_of_objects = []
                    list_of_objects.append(json.dumps(clientsharehandler, cls=share_handler.ClientShareHandlerEncoder))
                    list_of_objects.append(json.dumps(sharehandler, cls=share_handler.shareHandlerEncoder))
                    list_of_objects.append(json.dumps(client_share, cls=managingRequestfromClientEncoder))
                    udp_socket.sendto(json.dumps(list_of_objects).encode(),(lcr_obj.UID_IP_mapping[lcr_obj.leader_uid], 12347))
                    MY_HOST = socket.gethostname()
                    MY_IP = socket.gethostbyname(MY_HOST)
                    LEADER_HOST = MY_IP
                    setleaderstatus(False)
                    lcr_obj.election_done = False
                    lcr_obj.is_leader=False
                    FIRST_TIME = True
            


if __name__ == "__main__":
    sharehandler = None
    BROADCAST_IP = "192.168.0.255"
    # Perform leader election
    udp_socket_listener_for_election = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket_listener_for_election.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
    )
    udp_socket_listener_for_election.bind(("", 12347))
    udp_socket_listener_for_election.setblocking(False)
    
    lcr_obj = lcr_election_handler(
        get_machines_ip(), [], udp_socket_listener_for_election
    )
    is_leader, server_group = leader_election(SERVER_UDP_PORT, BROADCAST_IP, lcr_obj)
    setleaderstatus(is_leader)
    udp_thread = threading.Thread(
        target=udp_server, args=(SERVER_UDP_PORT, SERVER_TCP_PORT, getleaderstatus(), lcr_obj)
    )
    time.sleep(1)
    udp_thread.start()

    if getleaderstatus():
        sharehandler = share_handler.share_handler()
        #MY_HOST = socket.gethostname()
        #MY_IP = socket.gethostbyname(MY_HOST)
        clientsharehandler = share_handler.clientshare_handler(
                        0, 0, 'LEADER')
        client_share = managingRequestfromClient(
                        sharehandler, clientsharehandler, 'LEADER')
        setclientshareobject(client_share)
        clientobjectflag = True
        server_group.append((get_machines_ip(), SERVER_TCP_PORT))
        udp_thread_for_election = threading.Thread(target=udp_server_managing_election,
                                                   args=(udp_socket_listener_for_election, 
                                                         lcr_obj, getleaderstatus(), clientsharehandler, 
                                                         client_share, sharehandler))
    else:
        udp_thread_for_election = threading.Thread(target=udp_server_managing_election,
                                                   args=(udp_socket_listener_for_election, 
                                                         lcr_obj, getleaderstatus()))
        client_share = None
        server_group = ast.literal_eval(server_group)
        start_election(SERVER_UDP_PORT, BROADCAST_IP)

    udp_thread_for_election.start()
    # Start the TCP server (only if leader)
    tcp_server(SERVER_TCP_PORT, getleaderstatus(), client_share)
