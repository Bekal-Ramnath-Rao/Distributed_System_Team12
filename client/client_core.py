import argparse
import socket
import sys
from server.socket_handler import *

class Client():
    def __init__(self,broadcast_address,broadcast_port,args):
        super(Client,self).__init__()
        # Create a UDP socket
        self.udp_socket = configure_socket_UDP(False,True)               
        #Create a TCP socket
        self.tcp_socket = configuresocketTCP()
        self.buffer_size = 4096
        self.leader_address = self.server_connect(broadcast_address,broadcast_port,args)                       #Tuple representing the IP and Port of the leader server      
        #Connecting to the leader server   
        self.tcp_socket.connect(self.leader_address)

    def server_connect(self,broadcast_address,broadcast_port,arg):        
        message = 'Hi I am client,'+str(arg)
        # Send data
        sendmessagethroughUDP(self.udp_socket,message.encode(),(broadcast_address, broadcast_port))
        print('Sent to server: ', message)
        # Receive response
        print('Waiting for response...')
        data, server = self.udp_socket.recvfrom(self.buffer_size)
        print("Message received from leader at ",server)
        return server                                                

    def buy_sell_stocks(self,message):
        sendMessagethroughTCPSocket(self.tcp_socket,message)
        print("Sent Trading information & Waiting for response...")
        data,server = recvMessagefromTCPSocket(self.tcp_socket)
        print("Received response ",data)
        
    def close_connection(self):    
        self.tcp_socket.close()
        print('Socket Closed')

def main():
    arg = sys.argv
    broadcast_address = '<broadcast>'
    broadcast_port = 12345
    #queue = Queue()
    #Starting a Process
    #p = Process(target=Client, args=(broadcast_address, broadcast_port,arg,queue))
    #p.start()
    #p.join
    client_object = Client(broadcast_address,broadcast_port,arg[1])
    try:
        while True:
            user_input = input("Enter your activity ")
            if user_input.strip():
                client_object.buy_sell_stocks(user_input)
    except Exception as e:
            print(f"Error during trading: {e}") 
    finally:
        client_object.close_connection()

if __name__ == "__main__":
    main()
