class Server:

    pdfs: dict = {} # Dictionary: key=lobby-name, value pdf
    clients: dict = {} # Dictionary: key=ip of user, value=tupel(user-name,lobby)
    users: dict = {} # Dictionary: key=user-name, value=Status_Client
    changed: dict = {} # Dictionary: key=user-name, value=Boolean(changed in the last 2ms)


    def connect():
        # TODO
        pass


    def disconnect():
        # TODO
        pass


    def update_client_status():
        # TODO
        # users[user] = new Status_Client
        pass


    def send_server_status():
        server_status = Server_Status()

        for user in changed:
            if changed[user] is True:
                server_status.add_state(users[user])



    while True:
        # TODO check for new messages

        # TODO check if 2ms passed and if so send new client states to all other clients
        pass