import socket
import time
from threading import Thread
import sys
from src.MessageTyp import *
import pickle

class Server:

    def __init__(self):
        host = "blah"

    # Dictionary: key=lobby-name, value pdf
    pdfs: dict = {}

    # Dictionary: key=ip of user, value=tupel(user-name,lobby)
    clients: dict = {}
    
    # Dictionary: key=user-name, value=Status_Client
    users: dict = {}

    # Dictionary: key=user-name, value=Boolean(changed in the last 2ms)
    changed: dict = {}

    # Host for the server
    host = "localhost"

    # Ports for the server
    port_tcp = 4445
    port_udp = 4446

    # Lobby list
    lobbies: list = []

    def serv(self): 
        message_handler = MessageHandler(self)
        udp_server = UdpServer(message_handler, self.host, self.port_udp)
        tcp_server = TcpServer(message_handler, self.host, self.port_tcp)
        udp_server.start()
        tcp_server.start()

        while True:
            time.sleep(1)
            print(self.lobbies)

class TcpServer(Thread):

    host = ''
    port = -1

    def __init__(self, message_handler, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.message_handler = message_handler

    def run(self):
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        socket_.bind((self.host, self.port))

        while True:

            socket_.listen(1)

            conn, addr = socket_.accept()

            data = conn.recv(1024)
            newdata = conn.recv(1024)

            while len(newdata) > 0:
                data.append(newdata)
                newdata = conn.recv(1024)

            typ, obj = pickle.loads(data)

            self.message_handler.handle_message(obj)


        conn.close()

class UdpServer(Thread):

    host = ''
    port = -1

    def __init__(self, message_handler, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.message_handler = message_handler

    def run(self):
        try:
            socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket_.error as err_msg:
            print('Unable to instantiate socket_. Error message : ' + err_msg)
            sys.exit()

        socket_.bind((self.host, self.port))
        socket_.listen(1)

        conn, addr = socket_.accept()

        while True:
            data = conn.recvfrom(1024).decode()
            if not data:
                break
            print ("from connected  user: " + str(data))

            data = str(data).upper()
            print ("Received from User: " + str(data))

            data = input(" ? ")
            conn.send(data.encode())

        conn.close()

class MessageHandler:

    server: Server

    def __init__(self, server):
        self.server = server


    def handle_message(self, object_):
        if object_ is LobbyConnect:
            self.handle_lobby(object_)
        elif object_ is ClientStatus:
            self.handle_client_status(object_)


    def handle_lobby(self, lobby):
        self.server.lobbies.add(lobby)


    def handle_client_status(self, client_status):
        #self.server.users[client_status]
        pass
