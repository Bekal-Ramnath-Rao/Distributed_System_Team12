import socket
import threading
from share_handler import share_handler
from managing_request import managingRequestfromClient

def handle_client(conn, client_address, sharehandler, clientsharehandler):
    """Handle communication with a single client."""
    print(f"TCP connection established with {client_address}")
    try:
        while True:
            # Receive a message from the client
            client_message = conn.recv(1024).decode()
            if not client_message or client_message.lower() == "exit":
                print(f"Client {client_address} requested to close the connection.")
                break
            else:
                filtered_string = list(client_message.split())
                client_share = managingRequestfromClient(sharehandler, clientsharehandler)

                if 'b' == filtered_string[1]:
                    number_of_shares = int(filtered_string[3])
                    name_of_the_share = filtered_string[2]
                    transaction_result = client_share.executetheBuyrequest(number_of_shares, name_of_the_share)
                if 's' == filtered_string[1]:
                    number_of_shares = int(filtered_string[3])
                    name_of_the_share = filtered_string[2]
                    transaction_result = client_share.executetheSellrequest(number_of_shares, name_of_the_share)
                elif 'i' or 'I' in filtered_string[1]:
                    client_share.executetheInquiryrequest()

            print(f"Received message from {client_address}: {client_message}")

            # Send a response back to the client
            if(transaction_result):
                server_response = "Transaction successful"
                conn.send(server_response.encode())
            else:
                server_response = "Transaction failed"
                conn.send(server_response.encode())

            # Optionally terminate the connection if the server sends 'exit'
            if server_response.lower() == "exit":
                print(f"Closing connection with {client_address}.")
                break

    except Exception as e:
        print(f"Error with client {client_address}: {e}")
        conn.close()
        print(f"Connection closed with {client_address}.")

def tcp_server(tcp_port, sharehandler, clientsharehandler):
    """Handle multiple clients via TCP."""
    # Create a TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(('0.0.0.0', tcp_port))  # Bind to all interfaces
    tcp_socket.listen(5)  # Allow up to 5 clients to queue for connections
    print(f"Server is waiting for TCP connections on port {tcp_port}...")

    try:
        while True:
            # Accept a new connection
            conn, client_address = tcp_socket.accept()

            # Start a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(conn, client_address, sharehandler, clientsharehandler))
            client_thread.start()
            print(f"Started thread for client {client_address}")

    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        tcp_socket.close()
        print("TCP server closed.")

def udp_server(udp_port, tcp_port):
    """Handle UDP broadcast communication."""
    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind(('', udp_port))  # Listen on all interfaces

    print(f"Server is waiting for broadcast messages on UDP port {udp_port}...")

    while True:
        try:
            # Wait for a broadcast message
            message, client_address = udp_socket.recvfrom(4096)
            print(f"Received broadcast message '{message.decode()}' from {client_address}")

            # Send a unicast response to the client
            unicast_message = f"Hello Client, connect to me via TCP on port {tcp_port}"
            udp_socket.sendto(unicast_message.encode(), client_address)
            print(f"Sent unicast message to {client_address}: {unicast_message}")

        except KeyboardInterrupt:
            print("Shutting down UDP server.")
            break

    udp_socket.close()
    print("UDP server closed.")

if __name__ == '__main__':
    UDP_PORT = 12345
    TCP_PORT = 12346

    # Start the UDP server in the main thread
    udp_thread = threading.Thread(target=udp_server, args=(UDP_PORT, TCP_PORT))
    udp_thread.start()
    sharehandler = share_handler.share_handler()
    clientsharehandler = share_handler.clientshare_handler(0, 0)
    # Start the TCP server to handle multiple clients
    tcp_server(TCP_PORT, sharehandler, clientsharehandler)
