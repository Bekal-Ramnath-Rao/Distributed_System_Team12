import socket
import threading


# Client class
class HeartbeatClient:
    def __init__(self, port=12348):
        self.port = port

    def listen_broadcasts(self):
        """Listen for broadcast messages and respond to 'ARE YOU THERE'."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind(("", self.port))
            while True:
                data, addr = udp_socket.recvfrom(1024)
                message = data.decode()
                if message == "ARE YOU THERE":
                    print(f"Received broadcast from {addr}")
                    self.respond_to_server(addr)

    def respond_to_server(self, addr):
        """Send 'I AM THERE' response to the server."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            response = "I AM THERE"
            udp_socket.sendto(response.encode(), ("192.168.0.101",12348))
            print(f"Sent response to {addr}")

    def run(self):
        """Run the client thread."""
        threading.Thread(target=self.listen_broadcasts, daemon=True).start()


if __name__ == "__main__":
    client = HeartbeatClient()
    client.run()

    # Keep the main thread alive
    while True:
        pass
