class Server_Status:

    code: int
    message: String
    changed_users: dict = {}

    def __init__(self, code=0, message=None):
        self.code = code
        self.message = message

    def add_state(self, user_name, state: Client_Status):
        dict[user_name] = state