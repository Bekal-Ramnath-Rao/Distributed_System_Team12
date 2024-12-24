import socket
import threading
import time
from share_handler import share_handler
from managing_request import managingRequestfromClient

from election_handler import lcr_election_handler


LEADER_HOST = None  # The leader's host address (dynamically updated)
LEADER_TCP_PORT = None  # The leader's TCP port (dynamically updated)
SERVER_UDP_PORT = 12345
SERVER_TCP_PORT = 12346
TIMEOUT = 5  # Timeout for leader election (in seconds)

server_group = []  # List of (host, port) tuples for all servers in the group


def handle_client(conn, client_address, sharehandler):
    """Handle communication with a single client."""
    print(f"TCP connection established with {client_address}")
    flag = False
    try:
        while True:
            client_message = conn.recv(1024).decode()
            if not client_message or client_message.lower() == "exit":
                print(f"Client {client_address} requested to close the connection.")
                break
            else:
                # Process the request as the leader
                filtered_string = list(client_message.split())
                if flag == False:
                    clientsharehandler = share_handler.clientshare_handler(
                        0, 0, filtered_string[0]
                    )
                    client_share = managingRequestfromClient(
                        sharehandler, clientsharehandler, filtered_string[0]
                    )
                    flag = True

                if filtered_string[1] in ("b", "B"):
                    number_of_shares = int(filtered_string[3])
                    name_of_the_share = filtered_string[2]
                    transaction_result = client_share.executetheBuyrequest(
                        number_of_shares, name_of_the_share
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
                        number_of_shares, name_of_the_share
                    )
                    server_response = (
                        "Transaction successful"
                        if transaction_result
                        else "Transaction failed"
                    )
                    conn.send(server_response.encode())
                elif filtered_string[1] in ("i", "I"):
                    Data = client_share.executetheInquiryrequest()
                    Data = str(Data)
                    conn.send(Data.encode())

            print(f"Received message from {client_address}: {client_message}")

    except Exception as e:
        print(f"Error with client {client_address}: {e}")
        conn.close()
        print(f"Connection closed with {client_address}.")


def tcp_server(tcp_port, sharehandler, is_leader):
    """Handle multiple clients via TCP."""
    if not is_leader:
        print("This server is a follower and will not handle client requests.")
        return

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("0.0.0.0", tcp_port))  # Bind to all interfaces
    tcp_socket.listen(5)  # Allow up to 5 clients to queue for connections
    print(f"Leader server is listening on TCP port {tcp_port}...")

    try:
        while True:
            conn, client_address = tcp_socket.accept()
            client_thread = threading.Thread(
                target=handle_client, args=(conn, client_address, sharehandler)
            )
            client_thread.start()
            print(f"Started thread for client {client_address}")
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        tcp_socket.close()
        print("TCP server closed.")


def udp_server(udp_port, tcp_port, is_leader_flag):
    """Handle UDP communication for leader election, server group management, and client communication."""
    global LEADER_HOST, LEADER_TCP_PORT, server_group

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind(("", udp_port))  # Listen on all interfaces

    if is_leader_flag:
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

            if is_leader_flag:
                # Leader responds to server broadcast messages
                if message == "NEW_SERVER":
                    server_group.append(client_address)
                    unicast_message = f"ACK_LEADER {tcp_port}"
                    udp_socket.sendto(unicast_message.encode(), client_address)
                    print(f"Added new server {client_address} to the group.")
                # Handle client inquiries to identify the leader
                elif message == "WHO_IS_LEADER":
                    leader_info = f"LEADER {tcp_port}"
                    udp_socket.sendto(leader_info.encode(), client_address)
                    print(f"Sent leader information to client {client_address}.")
            else:
                # Followers listen for leader acknowledgment or respond to client inquiries
                if message.startswith("ACK_LEADER"):
                    leader_port = int(message.split()[1])
                    LEADER_HOST, LEADER_TCP_PORT = client_address[0], leader_port
                    print(f"Leader found at {LEADER_HOST}:{LEADER_TCP_PORT}.")
                elif message == "WHO_IS_LEADER":
                    if LEADER_HOST and LEADER_TCP_PORT:
                        leader_info = f"LEADER {LEADER_TCP_PORT}"
                        udp_socket.sendto(leader_info.encode(), client_address)
                        print(f"Sent leader information to client {client_address}.")

        except KeyboardInterrupt:
            print("Shutting down UDP server.")
            break

    udp_socket.close()
    print("UDP server closed.")


def leader_election(udp_port, broadcast_ip):
    """Perform leader election by broadcasting and waiting for a response."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print("Broadcasting leader election message...")
    udp_socket.sendto("NEW_SERVER".encode(), (broadcast_ip, udp_port))

    udp_socket.settimeout(TIMEOUT)
    try:
        message, server_address = udp_socket.recvfrom(4096)
        if message.decode().startswith("ACK_LEADER"):
            print("here", message.decode())
            leader_port = int(message.decode().split()[1])
            global LEADER_HOST, LEADER_TCP_PORT
            server_group = message.decode()[30:]
            LEADER_HOST, LEADER_TCP_PORT = server_address[0], leader_port
            print(f"Leader acknowledged at {LEADER_HOST}:{LEADER_TCP_PORT}.")
            print(f"server group is {server_group}")
            return False  # This server is not the leader
    except socket.timeout:
        print("No leader found. Declaring self as leader.")
        return True  # This server becomes the leader
    finally:
        udp_socket.close()


if __name__ == "__main__":
    BROADCAST_IP = "192.168.0.255"
    sharehandler = None

    # Perform leader election
    IS_LEADER = leader_election(SERVER_UDP_PORT, BROADCAST_IP)

    if IS_LEADER:
        sharehandler = share_handler.share_handler()

    # Start the UDP server in a separate thread
    udp_thread = threading.Thread(
        target=udp_server, args=(SERVER_UDP_PORT, SERVER_TCP_PORT, IS_LEADER)
    )
    udp_thread.start()

    # Start the TCP server (only if leader)
    tcp_server(SERVER_TCP_PORT, sharehandler, IS_LEADER)
