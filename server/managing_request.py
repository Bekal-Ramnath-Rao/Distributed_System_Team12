import socket_handler
from share_handler import share_handler
import json

class managingRequestfromClient:

    def __init__(self, sharehandler, clientsharehandler, name_of_the_client):
        self.sharehandler = sharehandler
        self.clientsharehandler = clientsharehandler
        self.name_of_the_client = name_of_the_client

    def getRequestfromclient(self):
        print("Listening to message from client who wants to trade")
        litsen_socket = socket_handler.configure_socket_UDP(litsen = True)
        data, client_address = litsen_socket.recvfrom(1024)
        return data, client_address
    
    def sendAcknowledgementforTrading(self, client_address, message, UDP_socket):
        socket_handler.sendmessagethroughUDP(UDP_socket, client_address, message)

    def getDatafromclientusingTCP(self, client_address):
        server_socket, client_socket = socket_handler.tcpsocketforServer(client_address)
        socket_handler.recvMessagefromTCPSocket(server_socket)

    def getinfofromtheRequest(self, data):
        filtered_string = list(data.replace(" ", ""))
        if 'b' or 'B' in filtered_string[0]:
            number_of_shares = str.translate(filtered_string[-1])
            name_of_the_share = filtered_string[1]
            return self.sharehandler.buy(number_of_shares, name_of_the_share)
        if 's' or 'S' in filtered_string[0]:
            number_of_shares = str.translate(filtered_string[-1])
            name_of_the_share = filtered_string[1]
            return self.sharehandler.sell(number_of_shares, name_of_the_share, self.clientsharehandler)
        elif 'i' or 'I' in filtered_string[0]:
            pass

    def executetheBuyrequest(self, number_of_shares, name_of_the_share, name_of_the_client):
        return self.sharehandler.buy(number_of_shares, name_of_the_share, self.clientsharehandler, name_of_the_client)

    def executetheSellrequest(self,number_of_shares, name_of_the_share, name_of_the_client):
        return self.sharehandler.sell(number_of_shares, name_of_the_share, self.clientsharehandler, name_of_the_client)
    
    def executetheInquiryrequest(self, name_of_the_client):
        return self.sharehandler.inquiry(self.clientsharehandler, name_of_the_client)

    def maketheReplication(self):
        'will be implemented once replication handler is implemented'

    def sendAcknowledgement(self,client_socket, message):
        socket_handler.sendMessagethroughTCPSocket(client_socket, message)

    def to_dict(self):
        return {
            "sharehandler": self.sharehandler,
            "clientsharehandler": self.clientsharehandler,
            "name_of_the_client": self.name_of_the_client
        }
    
    @classmethod
    def from_dict(cls, data):
        instance = cls(data["sharehandler"], data["clientsharehandler"], data["name_of_the_client"])
        return instance
    
    def __eq__(self, other):
        if isinstance(other, managingRequestfromClient):
            return self.sharehandler == other.sharehandler \
               and self.clientsharehandler == other.clientsharehandler \
               and self.name_of_the_client == other.name_of_the_client
        return False
    
# Custom JSON Encoder
class managingRequestfromClientEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, managingRequestfromClient) or isinstance(obj, share_handler.share_handler) or isinstance(obj, share_handler.share) or isinstance(obj, share_handler.clientshare_handler):  
            return obj.to_dict()  # Serialize using the to_dict method
        return super().default(obj)
