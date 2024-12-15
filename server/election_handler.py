import socket


class lcr_election_handler:
    def __init__(self, lcr):
        self.lcr = lcr
        self.members = (
            []
        )  # who will pass this list to this class? and these members are identified before or after the election starts?
        self.ring = []
        self.is_leader = False
        self.participant_id = None
        self.is_a_pariticipant = False
        self.ip = None
        self.port = None
        self.uid = None
        self.leader_uid = None

    # not sure if this message is required
    def handle(self, message):
        if message.type == "election":
            self.lcr.handle_election(message)
        elif message.type == "leader":
            self.lcr.handle_leader(message)
        else:
            print("Unknown message type: " + message.type)

    def form_ring(self, members):
        sorted_binary_ring = sorted([socket.inet_aton(member) for member in members])
        sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
        return sorted_ip_ring

    def get_neighbour(self, ring, current_node_ip, direction="left"):
        current_node_index = (
            ring.index(current_node_ip) if current_node_ip in ring else -1
        )
        if current_node_index != -1:
            if direction == "left":
                if current_node_index + 1 == len(ring):
                    return ring[0]
                else:
                    return ring[current_node_index + 1]
            else:
                if current_node_index == 0:
                    return ring[len(ring) - 1]
                else:
                    return ring[current_node_index - 1]
        else:
            return None

    def send_election_msg(self, participant_id, is_leader):
        # pack into JSON and send
        # use socket function implemented by ramnath here
        # use logging module to log the messages
        # ensure only one way messaging is present
        pass

    def initiate_election(self):
        self.is_a_pariticipant = False
        self.lcr.send_election_msg(self.participant_id, self.is_leader)
        print("Election initiated by: " + self.participant_id)

    def process_received_message(self, message):
        # from socket the message is received
        election_message = json.loads(data.decode())
        # self.send_election_msg needs a neighbour
        if election_message["is_leader"]:
            self.leader_uid = election_message["mid"]
            # forward received election message to left neighbour
            self.is_a_pariticipant = False
            self.send_election_msg(self.leader_uid, True)
            # ring_socket.sendto(json.dumps(election_message), neighbour)

        if election_message["mid"] < self.uid and not self.is_a_pariticipant:
            # new_election_message = {"mid": self.uid, "is_leader ": False}
            self.is_a_pariticipant = True
            # send received election message to left neighbour
            self.send_election_msg(self.uid, False)

        elif election_message["mid"] > self.uid:
            # send received election message to left neighbour
            self.is_a_pariticipant = True
            self.send_election_msg(self.uid, election_message["is_leader"])
            # ring_socket.sendto(json.dumps(election_message), neighbour)

        elif election_message["mid"] == self.uid:
            self.leader_uid = my_uid
            # new_election_message = {"mid": my_uid, "isLeader ": True}
            # send new election message to left neighbour
            self.is_a_pariticipant = False
            self.send_election_msg(self.uid, True)


# if __name__ == "__main__":
#     print("Testing the election_handler class")
#     # Add your test code here
#     # test the election_handler class
