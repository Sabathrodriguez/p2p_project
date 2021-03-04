import random
import ipaddress
from random import seed
from random import random
from socket import *
import math
import threading

class Node:
    always_on_socket = socket(AF_INET, SOCK_STREAM)
    def __init__(self):
        self.always_on_portnumber = self.find_free_port()[1]
        self.nodeIP = self.always_on_socket.getsockname()
        self.isLeader = True
        self.other_sockets = {}
        self.nodeID = self.find_free_port()[1]

    def getnodeIP(self):
        return self.nodeIP

    def getnodeport(self):
        return self.always_on_portnumber

    def serverStuff(self):
        #TODO: instead of connecting multiple clients, disconnent the client after first message and then listen for new clients
        self.always_on_socket.bind((self.nodeIP[0], self.always_on_portnumber))
        self.always_on_socket.listen(5)
        while True:
            print("The server is ready to receive")
            connectionSocket, addr = self.always_on_socket.accept()

            is_leader_sentence = connectionSocket.recv(1024).decode()
            if is_leader_sentence == "True":
                self.isLeader = False;
                not_leader_message = "True"
                connectionSocket.send(not_leader_message.encode())
            elif is_leader_sentence == "False":
                self.isLeader = True
                is_leader_message = "False"
                connectionSocket.send(is_leader_message.encode())

            while True:
                sentence = connectionSocket.recv(1024).decode()
                if not sentence: break
                print("message received")
                capitalizedSentence = sentence.upper()
                connectionSocket.send(capitalizedSentence.encode())

                another_file = connectionSocket.recv(1024).decode()
                if another_file == "no":
                    lastmessage  = "connection closed"
                    connectionSocket.send(lastmessage.encode())
                    print("closing connection")
                    connectionSocket.close()
                    break

    def find_free_port(self, interface='127.0.0.1', socket_family=AF_INET,
                       socket_type=SOCK_STREAM):
        """
        Ask the platform to allocate a free port on the specified interface, then
        release the socket and return the address which was allocated.

        Copied from ``twisted.internet.test.connectionmixins.findFreePort``.

        :param bytes interface: The local address to try to bind the port on.
        :param int socket_family: The socket family of port.
        :param int socket_type: The socket type of the port.

        :return: A two-tuple of address and port, like that returned by
            ``socket.getsockname``.
        """
        address = getaddrinfo(interface, 0)[0][4]
        probe = socket(socket_family, socket_type)
        try:
            probe.bind(address)
            return probe.getsockname()
        finally:
            probe.close()

    def clientStuff(self):
        while True:
            client_socket = socket(AF_INET, SOCK_STREAM)
            port = int(input("enter server port: "))
            client_socket.connect((self.getnodeIP()[0], port))
            print("connected to server")
            sentence = ""
            first_message = str(self.isLeader)
            client_socket.send(str(first_message).encode())
            first_message_rcv = client_socket.recv(1024)
            print("i am leader: " + str(first_message_rcv))
            try:
                while sentence != "quit":
                    sentence = input("Enter message to send to server: ")
                    client_socket.send(sentence.encode())
                    modifiedSentence = client_socket.recv(1024)
                    print("From Server: ", modifiedSentence.decode())
                    reconnect = input("need another file? (yes/no)")
                    client_socket.send(reconnect.encode())
                    if reconnect == "no":
                        print(client_socket.recv(1024).decode())
                        client_socket.close()
                        break
            except IOError:
                print("error")


peer = Node()
isleader = input("is this the first node?")

if isleader == "true" or isleader == "yes":
    print("server port # is: " + str(peer.getnodeport()))
    peer = threading.Thread(target=peer.serverStuff)
    peer.start()
else:
    print("here")
    peer = threading.Thread(target=peer.clientStuff)
    peer.start()

