import socket
from src.server.UdpServer import UdpServer
from src.server.TcpServer import TcpServer
from src.server.MessageHandler import MessageHandler
import time

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
    port_udp = 4445

    # Lobby list
    lobbies: list = []

    def run(self): 
        message_handler = MessageHandler(self)
        udp_server = UdpServer(message_handler, self.host, self.port_udp)
        tcp_server = TcpServer(message_handler, self.host, self.port_tcp)
        udp_server.start()
        tcp_server.start()

        while True:
            time.sleep(1)
            print(self.lobbies)

    def test(self):
        print("test")

