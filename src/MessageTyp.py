from typing import Tuple


class LobbyConnect:
    pdf: bytes = None
    user_id = None

    def __init__(self, lobby_name: str, password: str, username: str, pdf: bytes = None):
        self.password: str = password
        self.lobby_name: str = lobby_name
        self.username = username
        self.pdf = pdf


class ClientStatus:
    mouse_pos: Tuple[float, float]
    marker_objects = []
    test = None

    def __init__(self, mouse_pos: Tuple[float, float], user_id: int, user_name: str, marker_objects=[]):
        self.marker_objects = marker_objects
        self.mouse_pos = mouse_pos
        self.user_id = user_id
        self.user_name = user_name

