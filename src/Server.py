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
        host = "blah"

    # Dictionary: key=lobby-name, value pdf
    pdfs: dict = {}

    # Dictionary: key=user-id, value=Status_Client
    users: dict = {}

    # Dictionary: key=user-name, value=Boolean(changed in the last 2ms)
    changed: dict = {}

    # Dictionary: key=user-name, value=adress of the user
    addresses: dict = {}

    # Highest user id
    high_id = 0

    # Host for the server
    host = "localhost"

    # Ports for the server
    port_tcp = 4445
    port_udp = 4446

    # Lobby list
    lobbies: dict = {}

    def serv(self):

        message_handler = MessageHandler(self)
        udp_server = UdpServer(message_handler, self.host, self.port_udp, self)
        tcp_server = TcpServer(message_handler, self.host, self.port_tcp)
        udp_server.start()
        tcp_server.start()

        while True:
            time.sleep(0.03)

            stati = {}
            for user in self.users:
                if self.changed[user]:
                    stati[user] = self.users[user]
                else:
                    stati[user] = None

        udp_server.send(pickle.dumps(stati))


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
        self.conn.socket.settimeout(0.2)
        try:
            new_data = self.conn.recv(1024)
            while len(new_data) > 0:
                data.append(new_data)
                new_data = self.conn.recv(1024)
        except socket.timeout:
            self.conn.settimeout(old_timeout)
        obj = pickle.loads(data)
        data = self.server.message_handler.handle_message(obj)
        if type(data) is LobbyConnect:
            self.server.socket_.sendall(pickle.dumps(data))
        else:
            self.server.socket_.sendall(data)
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

    def handle_lobby(self, lobby: LobbyConnect):
        if not lobby.lobby_name in self.server.lobbies:
            lobby.user_id = self.server.high_id
            self.server.high_id += 1
            self.server.lobbies[lobby.lobby_name] = lobby
            return lobby
        else:
            return 1

    def handle_client_status(self, client_status):
        self.server.users[client_status.user_id] = client_status
        self.server.changed[client_status.user_id] = True


if __name__ == "__main__":
    server = Server()
    server.serv()
