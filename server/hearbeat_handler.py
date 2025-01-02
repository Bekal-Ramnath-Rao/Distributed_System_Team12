import socket
import time
import threading
import ast

class HeartbeatManager:
    def __init__(self, port=12348, global_data_obj=None, filter_server_group=None, setservergroupupdatedflag = None, lcr_obj = None):
        self.port = port
        self.client_list = []
        self.leader_ip = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(("", 12348))
        self.global_flag_obj = global_data_obj
        self.filter_server_group = filter_server_group
        self.setservergroupupdatedflag = setservergroupupdatedflag
        self.lcr_obj = lcr_obj

    def broadcast(self):
        """Broadcast 'ARE YOU THERE' to all clients."""
        # with socket.socket(
        #     socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        # ) as udp_socket:
        #     udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #     udp_socket.settimeout(0.2)
        while True:
            if self.global_flag_obj.getleaderflag() and not self.lcr_obj.is_a_pariticipant:
                message = "ARE YOU THERE"
                self.udp_socket.sendto(message.encode(), ("192.168.0.255", self.port))
                print("Broadcast sent: ARE YOU THERE")
                time.sleep(5)  # Wait 3 seconds before the next broadcast

    def listen_responses(self):
        """Listen for responses from clients."""
        counter = 0
        while True:
            if self.global_flag_obj.getleaderflag() and not self.lcr_obj.is_a_pariticipant:
                try:
                    # Temporary set to collect clients during the timeout period
                    temp_client_list = []
                    self.udp_socket.settimeout(5)  # Set a 3-second timeout for responses
                    #self.udp_socket.setblocking(False)
                    start_time = time.time()
                    while (time.time() - start_time) < 4:
                        print('timeout is ', self.udp_socket.gettimeout())
                        data, addr = self.udp_socket.recvfrom(1024)
                        if data.decode() == "I AM THERE":
                            # if not self.lcr_obj.is_a_pariticipant:
                            temp_client_list.append(addr[0])
                            print(f"Received response from {addr[0]}")

                    counter = counter + 1
                    if counter == 2:
                    # if not self.lcr_obj.is_a_pariticipant:
                        print("temp_client_list is ", temp_client_list)
                        client_list = self.filter_server_group(temp_client_list)
                        message = f"SERVER_GROUP {client_list}"
                        self.udp_socket.sendto(message.encode(), ("192.168.0.255", self.port))
                        print("sent latest serer group" , client_list)
                        counter = 0
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
        time.sleep(3)
        while True:
            try:
                temp_client_list = []
                if not self.global_flag_obj.getleaderflag():
                    start_time = time.time()
                    self.udp_socket.settimeout(5)
                    while (time.time() - start_time) < 5:
                        try:
                            data, addr = self.udp_socket.recvfrom(1024)
                            message = data.decode()
                            print(message)
                            if message == "ARE YOU THERE":
                                print(f"Received broadcast from {addr}")
                                self.respond_to_server(addr,start_time)
                            elif message.startswith("SERVER_GROUP"):
                                for server in ast.literal_eval(message[13:]):
                                    temp_client_list.append(server[0][0])
                                server_group_local = self.filter_server_group(temp_client_list)
                                for server in server_group_local:
                                    if addr[0] == server[0][0]:
                                        leader_info = server[0][0]
                                server_group_local.remove(leader_info)

                        except socket.timeout:
                            print('timeout of the socket')
                            self.lcr_obj.election_done = False
                            self.filter_server_group(server_group_local)
                            self.setservergroupupdatedflag(True)
            except:
                print('Main exception')



    def respond_to_server(self, addr, start_time):
        if not self.global_flag_obj.getleaderflag() and not self.lcr_obj.is_pariticipant and ((time.time() - start_time) > 5) :
            """Send 'I AM THERE' response to the server."""
            # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            response = "I AM THERE"
            self.udp_socket.sendto(response.encode(), addr)
            print(f"Sent response to {addr}")

