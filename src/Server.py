import socket
import time
import array
from threading import Thread
import concurrent.futures
import sys
from MessageTyp import LobbyConnect, ClientStatus
import pickle


class Server:

    def __init__(self):
        message_handler = MessageHandler(self)
        udp_server = UdpServer(message_handler, self.host, self.port_udp, self)
        tcp_server = TcpServer(message_handler, self.host, self.port_tcp)
        udp_server.start()
        tcp_server.start()

    # Host for the server
    host = "localhost"

    # Ports for the server
    port_tcp = 4454
    port_udp = 4455

    # user -> lobby dictionary
    _user: dict = {}

    # Lobby list
    _lobbies: dict = {}

    def add_lobby(self, pdf, name, first_user, password):
        lobby = Lobby(pdf, self, name, password)
        lobby.users[first_user] = None
        lobby.changed[first_user] = None
        self._lobbies[name] = lobby
        self._user[first_user] = lobby
        lobby.start()
        return lobby


class TcpServer(Thread):

    host = ''
    port = -1
    socket_: socket

    def __init__(self, message_handler, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.message_handler = message_handler

    def run(self):
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket_.bind((self.host, self.port))

        threads = []

        while True:

            self.socket_.listen(4)

            conn, addr = self.socket_.accept()
            # let a tcp-connection thread handle the received data
            connection_thread = TcpConnection(conn, addr, self)
            connection_thread.start()
            threads.append(connection_thread)

        for t in threads:
            t.join()


class TcpConnection(Thread):

    def __init__(self, conn, addr, server):
        Thread.__init__(self)
        self.ip, self.port = addr
        self.conn = conn
        self.server = server

    def run(self):
        data = self.conn.recv(1024)
        old_timeout = self.conn.gettimeout()
        self.conn.settimeout(0.2)
        try:
            new_data = self.conn.recv(1024)
            while len(new_data) > 0:
                data += new_data
                new_data = self.conn.recv(1024)
        except socket.timeout:
            self.conn.settimeout(old_timeout)
        obj = pickle.loads(data)
        data = self.server.message_handler.handle_message(obj)
        self.conn.sendall(pickle.dumps(data))
        self.conn.close()


class UdpServer(Thread):

    host = ''
    port = -1
    socket_: socket.socket

    def __init__(self, message_handler, host, port, server: Server):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.message_handler = message_handler
        self.server = server

        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_.bind((self.host, self.port))

    def _send_(self, tupel):
        send_data, user = tupel
        self.socket_.sendto(send_data, user)

    def send(self, send_data):
        print(send_data)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self._send_, [(send_data, user)
                                       for user in self.server.users])

    def run(self):
        while True:
            data, addr = self.socket_.recvfrom(2048).decode()

            obj = pickle.loads(data)

            if type(obj) is ClientStatus:
                self.server.addresses[obj.user_id] = addr

            data = self.message_handler.handle_message(obj)


class MessageHandler:

    server: Server

    def __init__(self, server):
        self.server = server

    def handle_message(self, object_):
        if type(object_) is LobbyConnect:
            return self.handle_lobby(object_)
        elif type(object_) is ClientStatus:
            return self.handle_client_status(object_)

    def handle_lobby(self, lobby_connect: LobbyConnect):
        # if the received lobby is a new lobby
        if not lobby_connect.lobby_name in self.server._lobbies and lobby_connect.pdf is not None:
            lobby_connect.user_id = 0
            lobby_connect.pdf = None
            self.server._lobbies[lobby_connect.lobby_name] = self.server.add_lobby(
                lobby_connect.pdf, lobby_connect.lobby_name, lobby_connect.user_id, lobby_connect.password)
            return lobby_connect
        elif lobby_connect.lobby_name in self.server._lobbies and lobby_connect.pdf is None and lobby_connect.password is self.server._lobbies[lobby_connect.lobby_name].password:
            lobby_connect.user_id = self.server._lobbies[lobby_connect.lobby_name].high_id
            self.server._lobbies[lobby_connect.lobby_name].high_id += 1
            lobby_connect.pdf = self.server._lobbies[lobby_connect.lobby_name].pdf
            self.server._lobbies[lobby_connect.lobby_name].users[lobby_connect.user_id] = None
            self.server._lobbies[lobby_connect.lobby_name].changed[lobby_connect.user_id] = None
            self.server._user[lobby_connect.user_id] = self.server._lobbies[lobby_connect.lobby_name]
        else:
            return 1

    def handle_client_status(self, client_status):
        lobby = self.server._user[client_status.user_id]
        lobby.users[client_status.user_id] = client_status
        lobby.changed[client_status.user_id] = True


class Lobby(Thread):
    def __init__(self, pdf, server, name, password):
        Thread.__init__(self)
        self.pdf = pdf
        self.server = server
        self.name = name
        self.password = password

    # Name
    name: str

    # Password
    pasword: str

    # PDF
    pdf: bytes

    # Dictionary: key=lobby-name, value pdf
    pdfs: dict = {}

    # Dictionary: key=user-id, value=Status_Client
    users: dict = {}

    # Dictionary: key=user-id, value=Boolean(changed in the last 2ms)
    changed: dict = {}

    # Dictionary: key=user-id, value=adress of the user
    addresses: dict = {}

    # Highest user id
    high_id = 1  # Starts at 1 because lobby creator automatically gets assigned 0

    def run(self):
        while True:
            time.sleep(0.03)  # Send server status to users every 1/30 seconds

            stati = {}
            for user in self.users:
                if self.changed[user]:
                    stati[user] = self.users[user]
                else:
                    # if user-status has not changed add key to dictionary with None as value cause a missing user means that the user disconnected
                    stati[user] = None

            self.server.udp_server.send(pickle.dumps(stati))


if __name__ == "__main__":
    Server()
