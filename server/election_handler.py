import socket
import uuid
import json


class lcr_election_handler:
    def __init__(self, ip, group_view, udp_socket_listener_for_election):
        self.group_view = group_view
        self.members = []  # group view
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
        sorted_binary_ring = sorted(
            [socket.inet_aton(member) for member in self.members]
        )
        sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
        self.ring = sorted_ip_ring

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
                    return self.get_tuple_by_ip(self.ring[0])
                else:
                    return self.get_tuple_by_ip(self.ring[current_node_index + 1])
            else:
                if current_node_index == 0:
                    return self.get_tuple_by_ip(self.ring[len(self.ring) - 1])
                else:
                    return self.get_tuple_by_ip(self.ring[current_node_index - 1])
        else:
            return None

    def send_election_msg(self, participant_id, is_leader):
        election_message = {"mid": str(participant_id), "is_leader": is_leader}
        print("neighbour ip", self.get_neighbour())
        self.udp_socket.sendto(
            json.dumps(election_message).encode(), (self.neighbour, 12347)
        )
        print('message sent -->',election_message)

    def initiate_election(self):
        self.is_a_pariticipant = False
        self.send_election_msg(self.uid, self.is_leader)
        print("Election initiated by: " + str(self.uid))

    def get_leader_status(self):
        return self.is_leader

    def process_received_message(self, message):
        election_message = json.loads(message.decode())
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
            # send new election message to left neighbour
            self.is_a_pariticipant = False
            self.send_election_msg(self.uid, True)
            self.election_done = True
