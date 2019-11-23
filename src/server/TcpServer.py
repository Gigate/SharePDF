import sys
from threading import Thread
import socket
import pickle
from src.server.MessageHandler import MessageHandler


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
