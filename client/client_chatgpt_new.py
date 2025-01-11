import socket
import time
error_flag = False
pending_message = ''
def tcp_client(server_ip, tcp_port):
    """Continue TCP communication with the leader server."""
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"Connecting to leader server {server_ip} on TCP port {tcp_port}...")
    tcp_socket.connect((server_ip, tcp_port))
    print("TCP connection established with the leader server.")

    try:
        while True:
            global pending_message
            if pending_message != '':
                tcp_socket.send(pending_message.encode())
                pending_message = ''
                server_response = tcp_socket.recv(1024).decode()
                print(f"Received response from server: {server_response}")

            client_message = input("Enter message to send to the server (type 'exit' to quit): ")
            tcp_socket.send(client_message.encode())

            if client_message.lower() == "exit":
                print("Closing connection as requested by the client.")
                break

            server_response = tcp_socket.recv(1024).decode()
            print(f"Received response from server: {server_response}")

            if server_response.lower() == "exit":
                print("Server closed the connection.")
                break

    except Exception as e:
        print(f"Error during TCP communication: {e}")
        error_flag = True
        pending_message = client_message
        print(pending_message)
    finally:
        tcp_socket.close()
        print("TCP connection closed.")
        return error_flag

def udp_client(broadcast_ip, udp_port):
    """Discover the leader server via UDP broadcast."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        # Broadcast WHO_IS_LEADER message
        broadcast_message = "WHO_IS_LEADER"
        print(f"Broadcasting message to {broadcast_ip}:{udp_port}...")
        udp_socket.sendto(broadcast_message.encode(), (broadcast_ip, udp_port))

        # Wait for response
        udp_socket.settimeout(5)  # Timeout for response
        response, server_address = udp_socket.recvfrom(4096)
        response_message = response.decode()
        print(f"Received response: '{response_message}' from {server_address}")

        if response_message.startswith("LEADER"):
            leader_port = int(response_message.split()[1])
            print(f"Leader identified at {server_address[0]}:{leader_port}")
            udp_socket.close()
            return tcp_client(server_address[0], leader_port)
        else:
            print("Unexpected response. Could not find the leader.")
            udp_socket.close()

    except socket.timeout:
        print("No response received. Leader could not be found.")
        udp_socket.close()

if __name__ == '__main__':
    BROADCAST_IP = '192.168.0.255'
    UDP_PORT = 12345
    time.sleep(1)
    error_flag = udp_client(BROADCAST_IP, UDP_PORT)

    while error_flag == True:
        error_flag = False
        error_flag = udp_client(BROADCAST_IP, UDP_PORT)
    
    print('Client finished')