import socket
import struct
import sys


def get_machines_ip():
    udp_socket_for_ip_retrieval = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket_for_ip_retrieval.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket_for_ip_retrieval.connect(
        ("8.8.8.8", 80)
    )  # Google's public DNS server (doesn't send actual data)
    print("local IP is ", udp_socket_for_ip_retrieval.getsockname()[0])
    return udp_socket_for_ip_retrieval.getsockname()[0]


multicast_group = "239.1.1.1"
server_address = ("", 1234)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Bind to the server address
sock.bind(server_address)

sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
sock.setsockopt(
    socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(get_machines_ip())
)

# group = socket.inet_aton(multicast_group)
# mreq = struct.pack("4sL", group, socket.INADDR_ANY)
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


mreq = struct.pack("4s4s", socket.inet_aton(multicast_group), socket.inet_aton(get_machines_ip()))
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Receive/respond loop
while True:
    print("\nwaiting to receive message")
    data, address = sock.recvfrom(1024)

    print("received %s bytes from %s" % (len(data), address))
    print(data)

    print("sending acknowledgement to", address)
    sock.sendto(bytearray("ack", "utf-8"), address)
