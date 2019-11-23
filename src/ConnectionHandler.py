import pickle
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from fitz import Document

from src.MessageTyp import LobbyConnect
from src.PdfDrawWidget import PdfDrawWidget


class _Connection:
    socket: socket = None
    is_tcp_socket = False

    hostname = None
    port = None

    def create_tcp_socket(self, hostname, port, timeout=3):
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect(hostname, port)
            self.socket.settimeout(timeout)
            self.is_tcp_socket = True
        except OSError:
            self.remove_socket()
            raise OSError

    def remove_socket(self):
        self.socket.close()
        self.socket = None

    def create_udp_socket(self, hostname, port):
        try:
            self.hostname = hostname
            self.port = port
            self.socket = socket(AF_INET, SOCK_DGRAM)
            self.is_tcp_socket = False
        except OSError:
            self.remove_socket()
            raise OSError


class ConnectionHandler:
    connection: _Connection = None

    user_id: int = None

    def __init__(self, pdf_widget: PdfDrawWidget):
        self.pdf_widget: PdfDrawWidget = pdf_widget

    def requestLobbyCreation(self, hostname, port, lobbyname, password, username, pdf) -> bool:
        if self.connection is not None:
            self.connection = _Connection()
        if self.connection.socket is None:
            try:
                self.connection.create_tcp_socket(hostname, port)
                lobbyconnect = LobbyConnect(lobbyname, password, username, pdf)
                self.connection.socket.sendall(pickle.dumps(lobbyconnect, 4))

                data = self.connection.socket.recv(1024)
                newdata = self.connection.socket.recv(1024)

                while len(newdata) > 0:
                    data.append(newdata)
                    newdata = self.connection.socket.recv(1024)

                obj = pickle.loads(data)

                if obj is int:
                    self.connection.remove_socket()
                    return False
                if obj is LobbyConnect:
                    self.user_id = obj.user_id

            except OSError:
                raise OSError
        else:
            self.connection.remove_socket()
            return self.requestLobbyCreation(hostname, port, password, username, pdf)

    def joinLobby(self, hostname, port, lobbyname, password, username) -> bool:
        if self.connection is not None:
            self.connection = _Connection()
        if self.connection.socket is None:
            try:
                self.connection.create_tcp_socket(hostname, port)
                lobbyconnect = LobbyConnect(lobbyname, password, username)
                self.connection.socket.sendall(pickle.dumps(lobbyconnect, 4))

                data = self.connection.socket.recv(1024)
                newdata = self.connection.socket.recv(1024)

                while len(newdata) > 0:
                    data.append(newdata)
                    newdata = self.connection.socket.recv(1024)

                obj = pickle.loads(data)

                if obj is int:
                    self.connection.remove_socket()
                    return False
                if obj is LobbyConnect:
                    self.user_id = obj.user_id
                    self.pdf_widget.loadDocument()


            except OSError:
                raise OSError
        else:
            self.connection.remove_socket()
            return self.joinLobby(hostname, port, password, username)

