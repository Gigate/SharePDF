from typing import Tuple

from fitz import Document


class LobbyConnect:
#    pdf: Document = None
    user_id = None

    def __init__(self, lobby_name: str, password: str, username: str, pdf: Document = None):
        self.password: str = password
        self.lobby_name: str = lobby_name
        self.username = username
 #       self.pdf = pdf


class ClientStatus:
    mouse_pos: Tuple[float, float]
    marker_objects = []
    test = None

    def __init__(self, mouse_pos: Tuple[float, float], user_id: int, marker_objects=[]):
        self.marker_objects = marker_objects
        self.mouse_pos = mouse_pos
        self.user_id = user_id


class ServerStatus:
    code: int
    message: str
    changed_users: dict = {}
    connect_events = []

    def __init__(self, code=0, message=None):
        self.code = code
        self.message = message
