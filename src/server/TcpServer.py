import sys
from threading import Thread
import socket
import pickle
from src.server.Server import Server
from src.server.MessageHandler import MessageHandler


class TcpServer(Thread):

    host = ''
    port = -1
    server: Server

    def __init__(self, server, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.server = server
        self.handler = MessageHandler(server)

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

            self.handler.handle_message(obj)


        conn.close()
