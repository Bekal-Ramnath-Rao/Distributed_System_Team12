import socket_handler
from share_handler import share_handler

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

    def executetheSellrequest(self,number_of_shares, name_of_the_share):
        return self.sharehandler.sell(number_of_shares, name_of_the_share, self.clientsharehandler, self.name_of_the_client)
    
    def executetheInquiryrequest(self, name_of_the_client):
        return self.sharehandler.inquiry(self.clientsharehandler, name_of_the_client)

    def maketheReplication(self):
        'will be implemented once replication handler is implemented'

    def sendAcknowledgement(self,client_socket, message):
        socket_handler.sendMessagethroughTCPSocket(client_socket, message)

