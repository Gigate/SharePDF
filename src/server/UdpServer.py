from threading import Thread
import socket
import sys
from src.server.Server import Server

class UdpServer(Thread):

    host = ''
    port = -1
    server: Server

    def __init__(self, server, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.server = server

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

