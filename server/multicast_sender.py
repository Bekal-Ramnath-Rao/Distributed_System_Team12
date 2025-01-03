import socket

def get_machines_ip():
    udp_socket_for_ip_retrieval = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket_for_ip_retrieval.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket_for_ip_retrieval.connect(
        ("8.8.8.8", 80)
    )  # Google's public DNS server (doesn't send actual data)
    print("local IP is ", udp_socket_for_ip_retrieval.getsockname()[0])
    return udp_socket_for_ip_retrieval.getsockname()[0]

MCAST_GRP = '239.1.1.1'
MCAST_PORT = 1234

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(get_machines_ip()))
print("Sending")
sock.sendto(bytearray("str()", "utf-8"), (MCAST_GRP, MCAST_PORT))

data, address = sock.recvfrom(1024)
print('received %s bytes from %s' % (len(data), address))
print(data)