from MessageHandler import Lobby, ClientStatus 
import Server

class MessageHandler:

    server: Server

    def __init__(self, server):
        self.server = server


    def handle_message(self, object_):
        if object_ is Lobby:
            self.handle_lobby(object_)
        elif object_ is ClientStatus:
            self.handle_client_status(object_)


    def handle_lobby(self, lobby):
        self.server.lobbies.add(lobby)


    def handle_client_status(self, client_status):
        #self.server.users[client_status]
        pass
