import pickle
import threading
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from typing import Optional, Callable, Any, Iterable, Mapping
from fitz import Document
from src.MessageTyp import LobbyConnect, ClientStatus
from src.PdfDrawWidget import PdfDrawWidget
from threading import Thread
import time


class _Connection:
    socket: socket = None
    is_tcp_socket = False

    hostname = None
    port = None

    def create_tcp_socket(self, hostname, port, timeout=3):
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.settimeout(timeout)
            self.socket.connect((hostname, port))
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


class UdpThreat(Thread):

    def __init__(self, pdf_widget: PdfDrawWidget, con: _Connection, user_id: int):
        super().__init__(self)
        self.pdf_widget = pdf_widget
        self.waiting = threading.Condition()
        self.con = con
        self.user_id = user_id

    def run(self) -> None:
        self.waiting.acquire()
        while True:
            self.waiting.wait()
            status = ClientStatus(self.pdf_widget.relativeMousePos, self.user_id)
            self.con.socket.sendto(pickle.dumps(status), (self.con.hostname, self.con.port))
            time.sleep(0.02)

    def notify_this(self):
        self.waiting.acquire()
        self.waiting.notify()
        self.waiting.release()


class ConnectionHandler:
    connection: _Connection = None

    user_id: int = None

    def __init__(self, pdf_widget: PdfDrawWidget = None):
        self.pdf_widget: PdfDrawWidget = pdf_widget

    def requestLobbyCreation(self, hostname, port, lobbyname, password, username, pdf) -> bool:
        if self.connection is None:
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
        if self.connection is None:
            self.connection = _Connection()
        if self.connection.socket is None:
            try:
                self.connection.create_tcp_socket(hostname, port)
                lobby_connect = LobbyConnect(lobbyname, password, username)
                self.connection.socket.sendall(pickle.dumps(lobby_connect, 4))

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
            return self.joinLobby(hostname, port, lobbyname, password, username)
