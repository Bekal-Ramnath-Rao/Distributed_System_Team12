import socket
import time
import threading
import ast

class HeartbeatManager:
    def __init__(self, port=12348, global_data_obj=None, filter_server_group=None, setservergroupupdatedflag = None):
        self.port = port
        self.client_list = []
        self.leader_ip = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(("", 12348))
        self.global_flag_obj = global_data_obj
        self.filter_server_group = filter_server_group
        self.setservergroupupdatedflag = setservergroupupdatedflag

    def broadcast(self):
        """Broadcast 'ARE YOU THERE' to all clients."""
        # with socket.socket(
        #     socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        # ) as udp_socket:
        #     udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #     udp_socket.settimeout(0.2)
        while True:
            if self.global_flag_obj.getleaderflag():
                server_group = self.filter_server_group()
                message = "ARE YOU THERE"
                self.udp_socket.sendto(message.encode(), ("192.168.0.255", self.port))
                print("Broadcast sent: ARE YOU THERE")
                time.sleep(2)  # Wait 3 seconds before the next broadcast
                print("global flag is ", self.global_flag_obj.getglobalflag())

    def listen_responses(self):
        """Listen for responses from clients."""
        while True:
            if self.global_flag_obj.getleaderflag():
                try:
                    # Temporary set to collect clients during the timeout period
                    temp_client_list = []
                    self.udp_socket.settimeout(5)  # Set a 3-second timeout for responses
                    #self.udp_socket.setblocking(False)
                    start_time = time.time()
                    while (time.time() - start_time) < 3:
                        print('timeout is ', self.udp_socket.gettimeout())
                        data, addr = self.udp_socket.recvfrom(1024)
                        if data.decode() == "I AM THERE":
                            temp_client_list.append(addr[0])
                            print(f"Received response from {addr[0]}")
                            print("Global flag is", self.global_flag_obj.getglobalflag())
                            
                        #except self.udp_socket.timeout:
                            # Timeout occurs, stop collecting and process the results
                            #break
                    # Update the main client list and call the filtered_group function
                    client_list = self.filter_server_group(temp_client_list)
                    message = f"SERVER_GROUP {client_list}"
                    self.udp_socket.sendto(message.encode(), ("192.168.0.255", self.port))
                except Exception as e:
                    print(f"Error in listen_responses: {e}")

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
        threading.Thread(target=self.listen_broadcasts, daemon=True).start()
        # threading.Thread(target=self.monitor_clients, daemon=True).start()
        # self.monitor_clients()

    
    def listen_broadcasts(self):
        """Listen for broadcast messages and respond to 'ARE YOU THERE'."""
        # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        #     udp_socket.bind(('', self.port))
        while True:
            try:
                if not self.global_flag_obj.getleaderflag():
                    start_time = time.time()
                    self.udp_socket.settimeout(5)
                    while (time.time() - start_time) < 2:
                        try:
                            data, addr = self.udp_socket.recvfrom(1024)
                            message = data.decode()
                            print(message)
                            if message == "ARE YOU THERE":
                                print(f"Received broadcast from {addr}")
                                self.respond_to_server(addr)
                            elif message.startswith("SERVER_GROUP"):
                                self.filter_server_group(ast.literal_eval(message[13:]))
                        except socket.timeout:
                            print('timeout of the socket')
                            self.setservergroupupdatedflag(True)
            except:
                print('Main exception')



    def respond_to_server(self, addr):
        if not self.global_flag_obj.getleaderflag():
            """Send 'I AM THERE' response to the server."""
            # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            response = "I AM THERE"
            self.udp_socket.sendto(response.encode(), addr)
            print(f"Sent response to {addr}")

