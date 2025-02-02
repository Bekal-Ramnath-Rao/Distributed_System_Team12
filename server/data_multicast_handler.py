import socket
import threading
import pickle
import ast
import json
from share_handler import share_handler
from managing_request import managingRequestfromClient
import copy
import struct
import time 
class MulticastHandler:
    def __init__(self, global_data, clientsharehandler, sharehandler, client_share, lcr_obj, doserialization,getleaderstatus, my_ip='0.0.0.0'):
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
        self.port = 12349
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


        # Create the UDP socket
        self.multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.my_ip))
        self.multicast_socket.bind(("", self.port))
        self.multicast_socket.setblocking(False)
        mreq = struct.pack("4s4s", socket.inet_aton(self.multicast_group), socket.inet_aton(self.my_ip))
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.setblocking(False)
        self.udp_socket.bind(("", 12350))

        self.sequence_number = 0
        self.received_sequence_number = 0
        self.expected_sequence_number = 0
        self.sequence_number_serialized_data_dict={}
        self.holdback_queue = []
        self.delivery_queue = []
        self.first_time = True



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
        start_time = time.time()
        data = None
        while (time.time() - start_time) < 1:
            try:
                data, addr = self.multicast_socket.recvfrom(4096)
            except BlockingIOError:
                pass
        if data:
            return data.decode(), addr
        else:
            return 'NO_DATA', None

    def receive_unicast_data(self):
        """
        Receive serialized data from the multicast group and deserialize it.
        :return: Deserialized objects.
        """
        start_time = time.time()
        data = None
        while (time.time() - start_time) < 1:
            try:
                data, addr = self.udp_socket.recvfrom(4096)
            except BlockingIOError:
                pass
        if data:
            return data.decode(), addr
        else:
            return 'NO_DATA', None

    def receive_sequence_request(self):
        """
        Receive serialized data from the multicast group and deserialize it.
        :return: Deserialized objects.
        """
        start_time = time.time()
        data = None
        while (time.time() - start_time) < 1:
            try:
                data, addr = self.udp_socket.recvfrom(4096)
            except BlockingIOError:
                pass
        print(data)
        if data:
            if data.decode() == 'MULTICAST PLEASE':
                return 'MULTICAST PLEASE', None 
            return int(data.decode().split(' ')[-1]), addr
        else:
            return 'NO_DATA', None

    def deserialize_data(self, message):
        return ast.literal_eval(message)
    
    def changeintheobject(self):
        if self.prev_sharehandler == self.sharehandler:
            return False
        else:
            return True

    def get_sequence_number_serialized_data_dict(self, sequence_number):
        return self.sequence_number_serialized_data_dict[sequence_number]
    
    def processthedata(self,local_receivedmessage, addr):
        print("expected sequence number is ",self.expected_sequence_number)
        deserialized_message = self.deserialize_data(local_receivedmessage)
        list_of_dicts = [json.loads(item) for item in deserialized_message]
        if self.clientsharehandler is not None:
            print("before ", self.clientsharehandler.number_of_shareA)
        self.clientsharehandler = share_handler.clientshare_handler.from_dict(list_of_dicts[0])
        self.received_sequence_number = int(list_of_dicts[-1])
        print("LIST OF DICTS IS ",list_of_dicts[-1])
        if self.received_sequence_number == self.expected_sequence_number:
            self.expected_sequence_number += 1
            self.sequence_number_serialized_data_dict[self.received_sequence_number] = list_of_dicts
        elif self.received_sequence_number > self.expected_sequence_number:
            self.holdback_queue.append(list_of_dicts)
            unicast_message = 'I NEED ' + str(self.expected_sequence_number)
            #request data from leader server
            self.udp_socket.sendto(unicast_message.encode(), (addr[0],12350))
        print('len of holdback queue', len(self.holdback_queue))
        if len(self.holdback_queue)!=0:
            holdback_queue_seq_number = self.holdback_queue[0][-1]
            if holdback_queue_seq_number == self.expected_sequence_number:
                for elements in self.holdback_queue:
                    holdback_queue_seq_number = int(elements[-1])
                    if holdback_queue_seq_number == self.expected_sequence_number:
                        self.expected_sequence_number += 1
                        self.sequence_number_serialized_data_dict[self.expected_sequence_number] = elements
                self.holdback_queue.clear()
            else:
                unicast_message = 'I NEED ' + str(self.expected_sequence_number)
                #request data from leader server
                self.udp_socket.sendto(unicast_message.encode(), (addr[0],12350))
        
        print("END Expected sequence number is ",self.expected_sequence_number)
            
            
        
        print("RECEIVED SEQUENCE NUMBER ", self.received_sequence_number)
        print("after ",self.clientsharehandler.number_of_shareA)
        self.sharehandler = share_handler.share_handler.from_dict(list_of_dicts[1])
        self.client_share = managingRequestfromClient(self.sharehandler, self.clientsharehandler, 'FOLLOWER')
        self.lcr_obj.IP_UID_mapping = list_of_dicts[3]
        self.lcr_obj.UID_IP_mapping = list_of_dicts[4]
        print("MULTICAST DATA RECEIVED")

        print("Dictionary is ",self.sequence_number_serialized_data_dict)

    def multicast_main(self):
        while True:
            if self.getleaderstatus():
                    requested_sequence_number, addr = self.receive_sequence_request()
                    print('requested sequence number ',requested_sequence_number)
                    if requested_sequence_number != 'NO_DATA':
                        if requested_sequence_number in self.sequence_number_serialized_data_dict.keys():
                            requested_data = self.sequence_number_serialized_data_dict[requested_sequence_number]
                            self.udp_socket.sendto(json.dumps(requested_data).encode(), addr)
                    if self.changeintheobject() or requested_sequence_number == 'MULTICAST PLEASE':
                        serailized_data = self.doserialization(self.clientsharehandler, self.sharehandler, self.client_share, self.lcr_obj)
                        serailized_data.append(str(self.sequence_number))
                        self.sequence_number_serialized_data_dict[self.sequence_number] = serailized_data
                        self.sequence_number += 1
                        
                        self.multicast_data_periodically(serailized_data)
                        self.prev_clientsharehandler = copy.deepcopy(self.clientsharehandler)
                        self.prev_sharehandler = copy.deepcopy(self.sharehandler)
                        self.prev_client_share = copy.deepcopy(self.client_share)
                        self.global_data.setnewserverjoinedflag(False)
            else:
                local_receivedmessage, addr1 = self.receive_multicast_data()
                local_receivedunicastmessage, addr2 = self.receive_unicast_data()
                if local_receivedmessage != 'NO_DATA' :
                    print("addr1 is ", addr1)
                    self.processthedata(local_receivedmessage, addr1)
                elif local_receivedunicastmessage!= 'NO_DATA' :
                    print("addr2 is ", addr2)
                    self.processthedata(local_receivedunicastmessage, addr2)                    
    
    def run(self):
        """Run the server threads."""
        threading.Thread(target=self.multicast_main, daemon=True).start()
