from fitz import Document


class Lobby:
    pdf: Document = None

    def __init__(self, lobbyname: str, password: str):
        self.password: str = password
        self.lobbyname: str = lobbyname


class ServerStatus:

    code: int
    message: str
    changed_users: dict = {}
    connect_events = []

    def __init__(self, code=0, message=None):
        self.code = code
        self.message = message

    def add_state(self, user_name, state: ClientStatus):
        dict[user_name] = state

class ClientStatus:
    y_axis : float
    mouse_pos : (float,float)
    marker_objects = []
