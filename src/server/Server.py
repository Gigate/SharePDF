import socket
from UdpServer import UdpServer
from TcpServer import TcpServer
import time

class Server:

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
    lobbies = []

    def run(self):
        udp_server = UdpServer(self, self.host, self.port_udp)
        tcp_server = TcpServer(self, self.host, self.port_tcp)
        udp_server.start()
        tcp_server.start()

        while True:
            time.sleep(1)
            print(self.lobbies)

