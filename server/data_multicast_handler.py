import socket
import threading
import pickle
import ast
import json
from share_handler import share_handler
from managing_request import managingRequestfromClient
import copy

class MulticastHandler:
    def __init__(self, global_data, clientsharehandler, sharehandler, client_share, lcr_obj, doserialization,getleaderstatus,getservergroupupdatedstatus, my_ip='0.0.0.0'):
        """
        Initialize the multicast handler.
        :param multicast_group: Multicast group IP address.
        :param port: Port number for UDP communication.
        :param local_interface: Local interface IP address to bind the socket.
        :param ttl: Time-to-live for multicast packets.
        """
        self.global_data = global_data
        self.lcr_obj = lcr_obj
        self.multicast_group = '239.1.1.1'
        self.port = 1234
        self.my_ip = my_ip
        self.clientsharehandler = clientsharehandler
        self.sharehandler = sharehandler
        self.client_share = client_share
        self.lcr_obj = lcr_obj
        self.prev_clientsharehandler = None
        self.prev_sharehandler = None
        self.prev_client_share = None
        self.lcr_obj = lcr_obj
        self.getleaderstatus = getleaderstatus
        self.doserialization = doserialization
        self.getservergroupupdatedstatus = getservergroupupdatedstatus


        # Create the UDP socket
        self.multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.my_ip))
        self.multicast_socket.bind(("", self.port))


    def serialize_objects(self, *objects):
        """
        Serialize multiple objects into a single binary blob.
        :param objects: Objects to serialize.
        :return: Serialized binary data.
        """
        return pickle.dumps(objects)

    def multicast_data_periodically(self, serialized_data):
        """
        Send serialized data to the multicast group.
        :param serialized_data: Binary data to send.
        """
        self.multicast_socket.sendto(json.dumps(serialized_data).encode(), (self.multicast_group, self.port))
        print(f"Data sent to multicast group {self.multicast_group}:{self.port}")

    def receive_multicast_data(self):
        """
        Receive serialized data from the multicast group and deserialize it.
        :return: Deserialized objects.
        """
        data, address = self.multicast_socket.recvfrom(65536)  # Buffer size for UDP packets
        print(f"Data received from {address}")
        return data.decode()
    
    def deserialize_data(self, message):
        return ast.literal_eval(message)

    def multicast_main(self):
        while True:
            if self.getleaderstatus():
                serailized_data = self.doserialization(self.clientsharehandler, self.sharehandler, self.client_share, self.lcr_obj)
                if not(self.clientsharehandler == self.prev_clientsharehandler \
                       and self.sharehandler == self.prev_sharehandler \
                       and self.client_share == self.prev_client_share \
                        or not self.getservergroupupdatedstatus()):
                    self.multicast_data_periodically(serailized_data)
                    self.prev_clientsharehandler = copy.copy(self.clientsharehandler)
                    self.prev_sharehandler = copy.copy(self.sharehandler)
                    self.prev_client_share = copy.copy(self.client_share)
                    #self.prev_lcr_obj = copy.copy(self.lcr_obj)
            else:
                local_receivedmessage = self.receive_multicast_data()
                deserialized_message = self.deserialize_data(local_receivedmessage)
                list_of_dicts = [json.loads(item) for item in deserialized_message]
                self.clientsharehandler = share_handler.clientshare_handler.from_dict(list_of_dicts[0])
                self.sharehandler = share_handler.share_handler.from_dict(list_of_dicts[1])
                # client_share = managingRequestfromClient.from_dict(list_of_dicts[2])
                self.client_share = managingRequestfromClient(self.sharehandler, self.clientsharehandler, 'FOLLOWER')
                self.lcr_obj.IP_UID_mapping = list_of_dicts[3]
                self.lcr_obj.UID_IP_mapping = list_of_dicts[4]
    
    def run(self):
        """Run the server threads."""
        threading.Thread(target=self.multicast_main, daemon=True).start()
        # threading.Thread(target=self.listen_broadcasts, daemon=True).start()
