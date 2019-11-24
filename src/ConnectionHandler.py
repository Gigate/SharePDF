import pickle as pickle
import threading
from io import BytesIO
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, timeout
from typing import Optional, Callable, Any, Iterable, Mapping, Dict
from fitz import Document
from MessageTyp import LobbyConnect, ClientStatus
from PdfDrawWidget import PdfDrawWidget
from threading import Thread
import fitz
import time


class _Connection:
    socket = None
    is_tcp_socket = False

    hostname = None
    port = None

    def create_tcp_socket(self, hostname, port, timeout=100):
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.settimeout(timeout)
            self.socket.connect((hostname, port))
            self.is_tcp_socket = True
        except OSError:
            self.remove_socket()
            raise OSError

    def remove_socket(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def create_udp_socket(self, hostname, port):
        try:
            self.hostname = hostname
            self.port = port
            self.socket = socket(AF_INET, SOCK_DGRAM)
            self.socket.connect((hostname, port))
            self.is_tcp_socket = False
        except OSError:
            self.remove_socket()
            raise OSError


class UdpSendThread(Thread):

    def __init__(self, pdf_widget: PdfDrawWidget, con: _Connection, user_id: int, username: str):
        Thread.__init__(self)
        self.pdf_widget = pdf_widget
        self.waiting = threading.Condition()
        self.con = con
        self.user_id = user_id
        self.username = username
        pdf_widget.mouse_move_notifier_send = self.notify_this

    def run(self) -> None:
        self.waiting.acquire()
        while True:
            if self.con.socket is not None:
                self.waiting.wait()
                status = ClientStatus(self.pdf_widget.relativeMousePos, self.user_id, self.username)
                self.con.socket.sendall(pickle.dumps(status))
                time.sleep(0.02)
            else:
                break
        self.waiting.release()

    def notify_this(self):
        self.waiting.acquire()
        self.waiting.notify()
        self.waiting.release()


class UdpReceiveThread(Thread):
    complete_dict: Dict = None

    def __init__(self, pdf_widget: PdfDrawWidget, con: _Connection, user_id: int):
        Thread.__init__(self)
        self.pdf_widget = pdf_widget
        self.waiting = threading.Condition()
        self.con = con
        self.user_id = user_id

    def run(self):
        loop = True
        while loop:
            if self.con.socket is not None:
                obj = pickle.loads(self.con.socket.recv(2048))
                if type(obj) is dict:
                    changed = False
                    if self.complete_dict is None:
                        self.complete_dict = obj
                        changed = True
                    for key in self.complete_dict:
                        if key not in obj:
                            self.complete_dict.pop(key)
                            changed = True
                    for key, val in obj.items():
                        if type(val) is ClientStatus:
                            self.complete_dict[key] = val
                            changed = True
                        elif val is None:
                            pass
                        else:
                            print(
                                "Could not parse server data (Invalid ClientStatus)")
                            loop = False
                            break
                    if changed:
                        self.pdf_widget.external_client_dict = self.complete_dict.copy()
                        self.pdf_widget.multi_user_mode = True
                        self.pdf_widget.update()
                else:
                    print("Could not parse server data (Invalid type) actual type is:", type(obj))
                    break
            else:
                break
        self.con.remove_socket()


class ConnectionHandler:
    connection: _Connection = None

    user_id: int = None

    udp_thread_recv: UdpReceiveThread = None
    udp_thread_send: UdpSendThread = None

    def __init__(self, pdf_widget: PdfDrawWidget = None):
        self.pdf_widget: PdfDrawWidget = pdf_widget

    def request_lobby_creation(self, hostname, port, lobby_name, password, username, pdf) -> bool:
        if self.connection is None:
            self.connection = _Connection()
        if self.connection.socket is None:
            try:
                self.connection.create_tcp_socket(hostname, port)
                with open(pdf, 'rb') as fd:
                    pdf_bytes = fd.read()
                lobby_connect = LobbyConnect(
                    lobby_name, password, username, pdf_bytes)
                self.connection.socket.sendall(pickle.dumps(lobby_connect, 4))

                data = self.connection.socket.recv(1024)
                old_timeout = self.connection.socket.gettimeout()
                self.connection.socket.settimeout(0.2)
                try:
                    new_data = self.connection.socket.recv(1024)

                    while len(new_data) > 0:
                        data += new_data
                        new_data = self.connection.socket.recv(1024)
                except timeout:
                    self.connection.socket.settimeout(old_timeout)

                obj = pickle.loads(data)
                print(obj)

                if type(obj) is int:
                    self.connection.remove_socket()
                    return False
                if type(obj) is LobbyConnect:
                    self.user_id = obj.user_id
                    self.connection.remove_socket()
                    self.connection.create_udp_socket(hostname, port+1)
                    self.udp_thread_recv = UdpReceiveThread(
                        self.pdf_widget, self.connection, self.user_id)
                    self.udp_thread_send = UdpSendThread(
                        self.pdf_widget, self.connection, self.user_id, username)

                    self.udp_thread_send.start()
                    self.udp_thread_recv.start()

            except OSError:
                raise OSError
        else:
            self.connection.remove_socket()
            return self.request_lobby_creation(hostname, port, lobby_name, password, username, pdf)
        return True


    def join_lobby(self, hostname, port, lobby_name, password, username) -> bool:
        if self.connection is None:
            self.connection = _Connection()
        if self.connection.socket is None:
            try:
                self.connection.create_tcp_socket(hostname, port)
                lobby_connect = LobbyConnect(lobby_name, password, username)
                self.connection.socket.sendall(pickle.dumps(lobby_connect, 4))

                data = self.connection.socket.recv(1024)
                old_timeout = self.connection.socket.gettimeout()
                self.connection.socket.settimeout(0.2)
                try:
                    new_data = self.connection.socket.recv(1024)

                    while len(new_data) > 0:
                        data += new_data
                        new_data = self.connection.socket.recv(1024)
                except timeout:
                    self.connection.socket.settimeout(old_timeout)

                obj = pickle.loads(data)
                print("object", obj)
                if type(obj) is int:
                    self.connection.remove_socket()
                    return False
                if type(obj) is LobbyConnect:
                    self.user_id = obj.user_id
                    self.pdf_widget.pdfVis = fitz.open(None, obj.pdf, "pdf")
                    self.pdf_widget.update()
                    self.connection.create_udp_socket(hostname, port+1)
                    self.udp_thread_recv = UdpReceiveThread(
                        self.pdf_widget, self.connection, self.user_id)
                    self.udp_thread_send = UdpSendThread(
                        self.pdf_widget, self.connection, self.user_id, username)

                    self.udp_thread_send.start()
                    self.udp_thread_recv.start()

            except OSError:
                raise OSError
        else:
            self.connection.remove_socket()
            return self.join_lobby(hostname, port, lobby_name, password, username)
        return True

if __name__ == "__main__":
    c = ConnectionHandler()
    # c.join_lobby("localhost", 4445, "blah", "v", "ritendiu")
    c.request_lobby_creation("localhost", 4445, "blah", "ti",
                             "test", "/home/jere/Downloads/02-Intelligent-Agents.pdf")
