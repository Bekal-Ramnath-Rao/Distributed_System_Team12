import socket
import time

def tcp_client(server_ip, tcp_port):
    """Continue TCP communication with the server."""
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"Connecting to server {server_ip} on TCP port {tcp_port}...")
    tcp_socket.connect((server_ip, tcp_port))
    print("TCP connection established with the server.")

    try:
        while True:
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
    finally:
        tcp_socket.close()
        print("TCP connection closed.")

def udp_client(broadcast_ip, udp_port):
    """Send a UDP broadcast message and receive a unicast response."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    broadcast_message = "Hello Server, this is a broadcast message from the client!"
    print(f"Sending broadcast message to {broadcast_ip}:{udp_port}")
    udp_socket.sendto(broadcast_message.encode(), (broadcast_ip, udp_port))

    unicast_response, server_address = udp_socket.recvfrom(4096)
    print(f"Received unicast response from server {server_address}: {unicast_response.decode()}")

    tcp_port = 12346  # Match server's TCP port
    udp_socket.close()
    tcp_client(server_address[0], tcp_port)

if __name__ == '__main__':
    BROADCAST_IP = '192.168.0.255'
    UDP_PORT = 12345

    time.sleep(1)
    udp_client(BROADCAST_IP, UDP_PORT)