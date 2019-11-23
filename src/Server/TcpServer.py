import sys
from threading import Thread
import socket

class TcpServer(Thread):

    host = ''
    port = -1

    def __init__(self, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port


    def run(self):
        try:
            socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket_.error as err_msg:
            print('Unable to instantiate socket_. Error code: ' +
                  str(err_msg[0]) + ' , Error message : ' + err_msg[1])
            sys.exit()
    
        socket_.bind((self.host, self.port))
        socket_.listen(1)
    
        conn, addr = socket_.accept()
    
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            print ("from connected  user: " + str(data))
                                                    
            data = str(data).upper()
            print ("Received from User: " + str(data))
    
            data = input(" ? ")
            conn.send(data.encode())
                                                    
        conn.close()