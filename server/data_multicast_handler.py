import socket
import threading

class MulticastHandler:
    def __init__(self, global_data, lcr_obj, my_ip='0.0.0.0'):
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

        # Create the UDP socket
        self.multicast_socket.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.multicast_socket.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.multicast_socket.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        self.multicast_socket.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.my_ip))


    def serialize_objects(self, *objects):
        """
        Serialize multiple objects into a single binary blob.
        :param objects: Objects to serialize.
        :return: Serialized binary data.
        """
        return pickle.dumps(objects)

    def multicast(self, serialized_data):
        """
        Send serialized data to the multicast group.
        :param serialized_data: Binary data to send.
        """
        self.sock.sendto(serialized_data, (self.multicast_group, self.port))
        print(f"Data sent to multicast group {self.multicast_group}:{self.port}")

    def receive_multicast_data(self):
        """
        Receive serialized data from the multicast group and deserialize it.
        :return: Deserialized objects.
        """
        data, address = self.sock.recvfrom(65536)  # Buffer size for UDP packets
        print(f"Data received from {address}")
        return pickle.loads(data)
    
    def multicast_main(self):
        if leader_flag:
            get_latest_data()
            sertilize data()  using do_serialization(), but here just function call should take place
            because passing them here again is not good as the data belongs to main class  
            even for do_serialization, remove the parameter passed
                if global, then no need to pass parameters
            multicast_data_periodically()
        else:
            receive_data_peridically()
            deserialize_data()
            update_data()
    
    def run(self):
        """Run the server threads."""
        threading.Thread(target=self.multicast_main, daemon=True).start()
        # threading.Thread(target=self.listen_broadcasts, daemon=True).start()

# Usage Example
if __name__ == "__main__":
    handler = MulticastHandler(local_interface='192.168.0.100')  # Replace with your actual local IP

    # Serialize objects
    serialized_data = handler.serialize_objects({"name": "Monkey"}, [1, 2, 3], "Test", 42)

    # Send serialized data
    handler.send(serialized_data)

    # Receive and deserialize data
    received_objects = handler.receive()
    print("Deserialized Objects:", received_objects)
