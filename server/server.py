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
import hearbeat_handler
import data_multicast_handler
import data_multicast_handler

from collections import defaultdict

# Initialize a count dictionary globally
ip_count = defaultdict(int)

class global_data_class:
    def __init__(self):
        self.global_flag = False
        self.leader_flag = False
        self.newserverjoined = False
    def getleaderflag(self):
        return self.leader_flag
    def setleaderflag(self,value):
        self.leader_flag = value
    def setglobalflag(self,value):
        self.global_flag = value
    def getnewserverjoinedflag(self):
        return self.newserverjoined
    def setnewserverjoinedflag(self, value):
        self.newserverjoined = value
    
def setservergroupupdatedflag(flag):
    global is_server_group_updated
    is_server_group_updated = flag

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
pending_ip_list = []
newserverjoined = False
tcp_connection_list=[]
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

def filter_server_group(client_list, lcr_obj):
    global	server_group, pending_ip_list
    """
    Filters the server group list based on the IP addresses present in the client list.

    Args:
        server_group (list of tuples): List containing tuples with (IP address, port, UID).
        client_list (list of tuples): List containing tuples with (IP address, port).

    Returns:
        list of tuples: Filtered server group list where only tuples with matching IP addresses remain.
    """
    client_list.append(get_machines_ip())
    client_list = list(set(client_list))
    if getleaderstatus():	
        pending_ip_list = list(set(pending_ip_list))
    else:
        pending_ip_list = []

    for each_ip in pending_ip_list:
        ip_count[each_ip] += 1
        if each_ip in client_list and ip_count[each_ip] > 2:
            pending_ip_list.remove(each_ip)
            ip_count[each_ip] = 0
        else:
            client_list.append(each_ip)
    # Retain only those tuples in the server group where the IP address matches
    if not lcr_obj.is_a_pariticipant:
        server_group = [server for server in server_group if server[0] in client_list]
    print("server group after filtering ", server_group)
    return server_group

def handle_client(conn, client_address,client_share = None, global_data=None):
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


def tcp_server(tcp_port, is_leader, client_share, global_data=None):
    """Handle multiple clients via TCP."""
    global tcp_connection_list
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("0.0.0.0", tcp_port))  # Bind to all interfaces
    tcp_socket.listen(5)  # Allow up to 5 clients to queue for connections
    print(f"Leader server is listening on TCP port {tcp_port}...")
   
    try:
        while True:
            if getleaderstatus():
                if getclientshareobject() is not None:
                    conn, client_address = tcp_socket.accept()
                    tcp_connection_list.append(conn)
                    client_thread = threading.Thread(
                        target=handle_client, args=(conn, client_address, getclientshareobject(), global_data)
                    )
                    client_thread.start()
                    print(f"Started thread for client {client_address}")

    except KeyboardInterrupt:
        print("Server is shutting down.")
        tcp_socket.close()
        print("TCP server closed.")


def udp_server(udp_port, tcp_port, is_leader_flag, lcr_obj=None, global_data=None):
    """Handle UDP communication for leader election, server group management, and client communication."""
    global LEADER_HOST, LEADER_TCP_PORT, server_group, is_server_group_updated, pending_ip_list

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
    
    while True:
        try:
            message, client_address = udp_socket.recvfrom(4096)
            message = message.decode()
            print(f"Received message '{message}' from {client_address}")

            if getleaderstatus():
                # Leader responds to server broadcast messages
                if message.startswith("NEW_SERVER"):
                    pending_ip_list.append(client_address[0])
                    received_uid = str(message.split()[2])
                    lcr_obj.create_IP_UID_mapping(client_address[0], received_uid)
                    server_group = update_ip_list(server_group, client_address, lcr_obj.IP_UID_mapping)
                    unicast_message = (
                        f"ACK_LEADER {tcp_port} SERVER_GROUP {server_group}"
                    )
                    udp_socket.sendto(unicast_message.encode(), client_address)
                    print(f"Added new server {client_address} to the group.")
                    print("current server group is ", server_group)
                    global_data.setnewserverjoinedflag(True)
                    lcr_obj.is_a_pariticipant=True
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
                    pending_ip_list = [server[0] for server in server_group]

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
                    pending_ip_list = [server[0] for server in server_group]
        except KeyboardInterrupt:
            print("Shutting down UDP server.")
            break

    udp_socket.close()
    print("UDP server closed.")


def update_ip_list(ip_list, new_tuple, IP_UID_mapping=None):
    # Create a dictionary to store the latest tuple for each unique IP address
    ip_dict = {ip: (ip, port, IP_UID_mapping[ip]) for ip, port, uid in ip_list}
    # Update the dictionary with the new tuple
    ip_dict[new_tuple[0]] = new_tuple[0], new_tuple[1], IP_UID_mapping[new_tuple[0]]
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
        setleaderstatus(True)
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
    udp_socket.close()


def server_reinitialise_UDPbuffer(udp_socket):
    udp_socket.close()
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind(("", 12347))  # Listen on all interfaces
    return udp_socket

def do_serialization(clientsharehandler, sharehandler, client_share, lcr_obj):
    """
    Serialize multiple objects into a single binary blob.
    :param objects: Objects to serialize.
    :return: Serialized binary data.
    """
    serialized_data = []
    serialized_data.append(json.dumps(clientsharehandler, cls=share_handler.ClientShareHandlerEncoder))
    serialized_data.append(json.dumps(sharehandler, cls=share_handler.shareHandlerEncoder))
    serialized_data.append(json.dumps(client_share, cls=managingRequestfromClientEncoder))
    serialized_data.append(json.dumps(lcr_obj.IP_UID_mapping))
    serialized_data.append(json.dumps(lcr_obj.UID_IP_mapping))
    return serialized_data.copy()

def udp_server_managing_election(udp_socket, lcr_obj, is_leader, clientsharehandler = None, client_share = None, sharehandler = None, globaldata= None):

    global is_server_group_updated, i_initiated_election, server_group, LEADER_HOST, LEADER_TCP_PORT, tcp_connection_list
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
            lcr_obj.election_done = False
            FIRST_TIME = False
            if i_initiated_election and not getleaderstatus():
                if len(server_group) == 1:
                    is_leader, server_group = leader_election(SERVER_UDP_PORT, BROADCAST_IP, lcr_obj)
                    setleaderstatus(is_leader)
                else:
                    lcr_obj.initiate_election()
                    i_initiated_election = False

        if not FIRST_TIME and not lcr_obj.election_done:
            lcr_obj.is_a_pariticipant = False
            try:
                while True:
                    data, addr = lcr_obj.udp_socket.recvfrom(4096)  # Buffer size of 1024 bytes
                    print(f"Received message: {data.decode()} from {addr}")
                    latest_message = data
            except BlockingIOError:
            # This exception occurs when the buffer is empty
                if latest_message is not None:
                    print("\nBuffer is empty. Processing the latest message:")
                    lcr_obj.process_received_message(latest_message)
                    latest_message = None  # Reset after processing

        elif not FIRST_TIME and lcr_obj.election_done:
            if lcr_obj.get_leader_status():
                if not getleaderstatus():
                    try:
                        while True:
                            received_data, addr = lcr_obj.udp_socket.recvfrom(4096)  # Buffer size of 1024 bytes
                            print(f"Received message: {received_data.decode()} from {addr}")
                            latest_message = received_data
                        
                    except BlockingIOError:
                        # This exception occurs when the buffer is empty
                        if latest_message is not None:
                            print("\nBuffer is empty. Processing the latest message:")
                            deserialized_object = latest_message.decode()
                            deserialized_object_list  = ast.literal_eval(deserialized_object)
                            list_of_dicts = [json.loads(item) for item in deserialized_object_list]
                            print("Received serialized object list from leader", list_of_dicts)
                            clientsharehandler = share_handler.clientshare_handler.from_dict(list_of_dicts[0])
                            sharehandler = share_handler.share_handler.from_dict(list_of_dicts[1])
                            client_share = managingRequestfromClient(sharehandler, clientsharehandler, 'FOLLOWER')
                            lcr_obj.IP_UID_mapping = list_of_dicts[3]
                            lcr_obj.UID_IP_mapping = list_of_dicts[4]
                            setleaderstatus(True)
                            global_data.setleaderflag(True)
                            setclientshareobject(client_share) 
                            setclientsharehandlerobject(clientsharehandler)                    
                            FIRST_TIME = True
                            lcr_obj.election_done = False
                            lcr_obj.is_leader=True
                            FIRST_TIME = True
                            latest_message = None  # Reset after processing

            else:
                if getleaderstatus():
                    serialized_objects = do_serialization(clientsharehandler, sharehandler, client_share, lcr_obj)
                    udp_socket.sendto(json.dumps(serialized_objects).encode(),(lcr_obj.UID_IP_mapping[lcr_obj.leader_uid], 12347))
                    MY_HOST = socket.gethostname()
                    MY_IP = socket.gethostbyname(MY_HOST)
                    LEADER_HOST = MY_IP
                    setleaderstatus(False)
                    global_data.setleaderflag(False)
                    lcr_obj.election_done = False
                    lcr_obj.is_leader=False
                    FIRST_TIME = True
                    print("tcp_connection_list", tcp_connection_list)
                    for conn in tcp_connection_list:
                        conn.close()


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
    global_data = global_data_class()
    global_data.setleaderflag(is_leader)
    udp_thread = threading.Thread(
        target=udp_server, args=(SERVER_UDP_PORT, SERVER_TCP_PORT, getleaderstatus(), lcr_obj, global_data)
    )
    time.sleep(1)
    udp_thread.start()

    if getleaderstatus():
        sharehandler = share_handler.share_handler()
        clientsharehandler = share_handler.clientshare_handler(
                        0, 0, 'LEADER')
        client_share = managingRequestfromClient(
                        sharehandler, clientsharehandler, 'LEADER')
        setclientshareobject(client_share)
        clientobjectflag = True
        server_group.append((get_machines_ip(), SERVER_TCP_PORT, str(lcr_obj.uid)))
        udp_thread_for_election = threading.Thread(target=udp_server_managing_election,
                                                   args=(udp_socket_listener_for_election, 
                                                         lcr_obj, getleaderstatus(), clientsharehandler, 
                                                         client_share, sharehandler,global_data))
        heartbeat = hearbeat_handler.HeartbeatManager(12348, global_data, filter_server_group, setservergroupupdatedflag, lcr_obj, leader_election)
        heartbeat.run()
        multicaster = data_multicast_handler.MulticastHandler(global_data, clientsharehandler, sharehandler, client_share, lcr_obj, do_serialization,getleaderstatus,get_machines_ip())
        multicaster.run()
    else:
        udp_thread_for_election = threading.Thread(target=udp_server_managing_election,
                                                   args=(udp_socket_listener_for_election,
                                                         lcr_obj, getleaderstatus(),None,None, None, global_data))
        client_share = None
        server_group = ast.literal_eval(server_group)
        heartbeat = hearbeat_handler.HeartbeatManager(12348, global_data, filter_server_group, setservergroupupdatedflag, lcr_obj, leader_election)
        heartbeat.run()
        start_election(SERVER_UDP_PORT, BROADCAST_IP)
        multicaster = data_multicast_handler.MulticastHandler(global_data, None, None, None, lcr_obj, do_serialization,getleaderstatus,get_machines_ip())
        multicaster.run()
    
    lcr_obj.create_IP_UID_mapping(get_machines_ip(), str(lcr_obj.uid))

    udp_thread_for_election.start()
    # Start the TCP server (only if leader)
    tcp_server(SERVER_TCP_PORT, getleaderstatus(), client_share, global_data)
