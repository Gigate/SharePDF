import socket
from UdpServer import UdpServer
from TcpServer import TcpServer
import ServerStatus

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

    def run(self):
       # udp_server = UdpServer(self.host, self.port_udp)
        tcp_server = TcpServer(self.host, self.port_tcp)
      #  udp_server.start()
        tcp_server.start()

Server().run()


"""     def connect():
        # TODO
        pass

    def disconnect():
        # TODO
        pass

    def update_client_status():
        # TODO
        # users[user] = new Status_Client
        pass

    def send_server_status():
        server_status = ServerStatus() 

        for user in changed:
            if changed[user] is True:
                server_status.add_state(users[user]) """


