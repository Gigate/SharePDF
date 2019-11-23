from fitz import Document

class Lobby:
    abbr = "lby"
    pdf: Document = None

    def __init__(self, lobbyname: str, password: str):
        self.password: str = password
        self.lobbyname: str = lobbyname


class ClientStatus:
    abbr = "cst"
    mouse_pos : (float,float)
    marker_objects = []
    test = None

    def __init__(self, mouse_pos , marker_objects= []):
        self.marker_objects = marker_objects
        self.mouse_pos = mouse_pos


class ServerStatus:
    abbr = "cst"
    code: int
    message: str
    changed_users: dict = {}
    connect_events = []

    def __init__(self, code=0, message=None):
        self.code = code
        self.message = message

    def add_state(self, user_name, state: ClientStatus):
        dict[user_name] = state
