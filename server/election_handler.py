import socket
import uuid
import json


class lcr_election_handler:
    # which port to pass here?
    def __init__(self, ip, group_view, udp_socket_listener_for_election):
        # self.lcr = lcr
        self.group_view = group_view
        self.members = []  # group view
        # who will pass this list to this class? and these members are identified before or after the election starts?
        self.ring = []
        self.is_leader = False
        self.participant_id = None
        self.is_a_pariticipant = False
        self.ip = ip
        self.port = None
        self.uid = uuid.uuid1()  # Generating a Version 1 UUID
        self.leader_uid = None
        self.udp_socket = udp_socket_listener_for_election
        self.neighbour = None
        self.election_done = False
        self.IP_UID_mapping = {}
        self.UID_IP_mapping = {}
        print('my id is : ', self.uid)

    def create_IP_UID_mapping(self, client_address, uid):
        self.IP_UID_mapping[client_address] = str(uid)
        self.UID_IP_mapping[str(uid)] = client_address

    def form_members(self, group_view):
        self.members = [item[0] for item in group_view]

    def form_ring(self):
        # server core can call this function to form a ring
        sorted_binary_ring = sorted(
            [socket.inet_aton(member) for member in self.members]
        )
        # print(sorted_binary_ring)
        sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
        self.ring = sorted_ip_ring
        # return sorted_ip_ring

    def get_tuple_by_ip(self, ip_address):
        for item in self.group_view:
            if item[0] == ip_address:
                return item
        return None

    def get_neighbour(self, direction="left"):
        current_node_index = self.ring.index(self.ip) if self.ip in self.ring else -1
        if current_node_index != -1:
            if direction == "left":
                if current_node_index + 1 == len(self.ring):
                    # return self.ring[0]
                    return self.get_tuple_by_ip(self.ring[0])
                else:
                    return self.get_tuple_by_ip(self.ring[current_node_index + 1])
                    # return self.ring[current_node_index + 1]
            else:
                if current_node_index == 0:
                    return self.get_tuple_by_ip(self.ring[len(self.ring) - 1])
                else:
                    return self.get_tuple_by_ip(self.ring[current_node_index - 1])
        else:
            return None

    def send_election_msg(self, participant_id, is_leader):
        # pack into JSON and send
        # use socket function implemented by ramnath here
        # use logging module to log the messages
        # ensure only one way messaging is present
        election_message = {"mid": str(participant_id), "is_leader": is_leader}
        # here we need the neighbouring server's socket, fetch the TCP socket of neighbour from the dictionary ip_vs_tcp_socket_mapping
        # sendMessagethroughTCPSocket(
        #     client_socket, json.dumps(election_message).encode()
        # )
        print("neighbour ip", self.get_neighbour())
        self.udp_socket.sendto(
            json.dumps(election_message).encode(), (self.neighbour, 12347)
        )
        print('message sent -->',election_message)

    def initiate_election(self):
        self.is_a_pariticipant = False

        # self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.send_election_msg(self.uid, self.is_leader)
        print("Election initiated by: " + str(self.uid))

    def get_leader_status(self):
        return self.is_leader

    def process_received_message(self, message):
        # from socket the message is received
        election_message = json.loads(message.decode())
        # print("Received message: " + str(election_message))

        # self.send_election_msg needs a neighbour
        if election_message["is_leader"]:
            self.leader_uid = election_message["mid"]
            # forward received election message to left neighbour
            self.is_a_pariticipant = False
            if (self.uid != self.leader_uid):
                self.is_leader = False
            print("Election completed, leader is: " + str(self.leader_uid))
            if len(self.members) > 2:
                self.send_election_msg(self.leader_uid, True)
            self.election_done = True

        if election_message["mid"] < str(self.uid) and not self.is_a_pariticipant:
            # new_election_message = {"mid": self.uid, "is_leader ": False}
            self.is_a_pariticipant = True
            # send received election message to left neighbour
            self.send_election_msg(self.uid, False)

        elif election_message["mid"] > str(self.uid) and not self.election_done:
            # send received election message to left neighbour
            self.is_a_pariticipant = True
            self.send_election_msg(
                election_message["mid"], election_message["is_leader"]
            )

        elif election_message["mid"] == str(self.uid):
            print("Election completed, leader is: " + str(self.uid))
            self.leader_uid = self.uid
            self.is_leader = True
            # new_election_message = {"mid": my_uid, "isLeader ": True}
            # send new election message to left neighbour
            self.is_a_pariticipant = False
            self.send_election_msg(self.uid, True)
            self.election_done = True


# if __name__ == "__main__":
#     handlers = []
#     from unittest.mock import patch, MagicMock

#     def run_tests():
#         # Mock socket methods
#         with patch("socket.inet_aton") as mock_inet_aton, patch(
#             "socket.inet_ntoa"
#         ) as mock_inet_ntoa:
#             # Prepare mock data
#             mock_aton_results = {
#                 "192.168.0.1": b"\xc0\xa8\x00\x01",
#                 "192.168.0.2": b"\xc0\xa8\x00\x02",
#                 "192.168.0.3": b"\xc0\xa8\x00\x03",
#                 "192.168.0.4": b"\xc0\xa8\x00\x04",
#                 "192.168.0.5": b"\xc0\xa8\x00\x05",
#             }
#             mock_inet_aton.side_effect = lambda ip: mock_aton_results[ip]
#             mock_inet_ntoa.side_effect = lambda binary: {
#                 v: k for k, v in mock_aton_results.items()
#             }[binary]

#             # Create instances
#             ips = [
#                 "192.168.0.5",
#                 "192.168.0.1",
#                 "192.168.0.4",
#                 "192.168.0.2",
#                 "192.168.0.3",
#             ]
#             # nodes = [lcr_election_handler(ip) for ip in ips]
#             for i, server in enumerate(ips):
#                 handler = lcr_election_handler(server)
#                 handler_name = "s" + str(i + 1)
#                 globals()[handler_name] = handler
#                 handlers.append(handler)

#             for i in handlers:
#                 i.members = [
#                     "192.168.0.5",
#                     "192.168.0.1",
#                     "192.168.0.4",
#                     "192.168.0.2",
#                     "192.168.0.3",
#                 ]

#             # print(handlers)
#             # Assign members to each node and form the ring
#             for node in handlers:
#                 node.form_ring()

#             # print(nodes[0].ring)
#             print(s4.ring)

#             # exit()

#             # s1.uid = "5ee22f6c-bbca-11ef-a9b0-5cea1d0f55fa"
#             # s2.uid = "6ee22f6c-bbca-11ef-a9b0-5cea1d0f55fb"
#             # if s1.uid < s2.uid:
#             #     print("s1 is less") #just to check whether uid comparison is same as string comparison

#             # data = {
#             #     "mid": "5ee22f6c-bbca-11ef-a9b0-5cea1d0f55fa",
#             #     "is_leader": False,
#             # }
#             # s1.process_received_message(json.dumps(data).encode())  # this checks if the node itself is a leader

#             # data = {
#             #     "mid": "6ee22f6c-bbca-11ef-a9b0-5cea1d0f55fb",
#             #     "is_leader": False,
#             # }
#             # s1.process_received_message(json.dumps(data).encode()) #this checks if the node has uid less than received servers uid

#             # data = {
#             #     "mid": "5ee22f6c-bbca-11ef-a9b0-5cea1d0f55fa",
#             #     "is_leader": False,
#             # }
#             # s2.process_received_message(json.dumps(data).encode()) #this checks if the node has uid greater than received servers uid

#             # data = {
#             #     "mid": "6ee22f6c-bbca-11ef-a9b0-5cea1d0f55fb",
#             #     "is_leader": True,
#             # }
#             # s1.process_received_message(json.dumps(data).encode())

#     run_tests()
