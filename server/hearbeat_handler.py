import socket
import time
import threading

class HeartbeatManager:
    def __init__(self, port=12348, global_data_obj=None):
        self.port = port
        self.client_list = []
        self.leader_ip = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(("", 12348))
        self.global_flag_obj = global_data_obj

    def broadcast(self):
        """Broadcast 'ARE YOU THERE' to all clients."""
        # with socket.socket(
        #     socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        # ) as udp_socket:
        #     udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #     udp_socket.settimeout(0.2)
        while True:
            if self.global_flag_obj.getglobalflag():
                message = "ARE YOU THERE"
                self.udp_socket.sendto(message.encode(), ("127.0.0.1", self.port))
                print("Broadcast sent: ARE YOU THERE")
                time.sleep(2)  # Wait 3 seconds before the next broadcast
                print("global flag is ", self.global_flag_obj.getglobalflag())

    def listen_responses(self):
        """Listen for responses from clients."""
        # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        #     udp_socket.bind(("", self.port))
        #     udp_socket.settimeout(3)  # 3-second timeout for responses
        while True:
            try:
                # self.udp_socket.settimeout(3)
                if self.global_flag_obj.getglobalflag():
                    data, addr = self.udp_socket.recvfrom(1024)
                    if data.decode() == "I AM THERE":
                        # with self.lock:
                        self.client_list.add(addr[0])
                        print(f"Received response from {addr[0]}")
                        print("global flag is ", self.global_flag)
            except socket.timeout:
                pass

    def monitor_clients(self):
        """Monitor the list of active clients."""
        while True:
            time.sleep(3)
            # with self.lock:
            if self.client_list:
                print(f"Active clients: {self.client_list}")
            else:
                print("No active clients.")
            self.client_list.clear()

    def run(self):
        """Run the server threads."""
        threading.Thread(target=self.broadcast, daemon=True).start()
        threading.Thread(target=self.listen_responses, daemon=True).start()
        # threading.Thread(target=self.listen_broadcasts, daemon=True).start()
        # threading.Thread(target=self.respond_to_server, daemon=True).start()
        # threading.Thread(target=self.monitor_clients, daemon=True).start()
        # self.monitor_clients()

    
    def listen_broadcasts(self):
        """Listen for broadcast messages and respond to 'ARE YOU THERE'."""
        # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        #     udp_socket.bind(('', self.port))
        while True:
            data, addr = self.udp_socket.recvfrom(1024)
            message = data.decode()
            if message == "ARE YOU THERE":
                print(f"Received broadcast from {addr}")
                self.respond_to_server(addr)

    def respond_to_server(self, addr):
        """Send 'I AM THERE' response to the server."""
        # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        response = "I AM THERE"
        self.udp_socket.sendto(response.encode(), (self.leader_ip, self.port))
        print(f"Sent response to {addr}")

