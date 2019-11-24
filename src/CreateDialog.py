import sys

from PyQt5.QtWidgets import QDialog, QApplication, QDialogButtonBox, QVBoxLayout, QMainWindow, QInputDialog, QLineEdit, \
    QPushButton, QLabel, QMessageBox, QCheckBox


class CreateLobbyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.title = 'JoinLobby'
        self.left = 100
        self.top = 100
        self.width = 350
        self.height = 200
        self.initUI()
        #text input
        self.textbox_lobby = QLineEdit(self)
        self.textbox_lobby.move(100, 15)
        self.textbox_lobby.resize(200, 25)

        self.textbox_user = QLineEdit(self)
        self.textbox_user.move(100, 50)
        self.textbox_user.resize(200, 25)

        self.textbox_password = QLineEdit(self)
        self.textbox_password.move(100, 85)
        self.textbox_password.resize(200, 25)
        self.textbox_password.setEchoMode(QLineEdit.Password)
        #Label
        labelLobby = QLabel(self)
        labelLobby.setText('Lobbyname:')
        labelLobby.move(20, 20)

        label_user = QLabel(self)
        label_user.setText('Username:')
        label_user.move(20, 55)

        label_password = QLabel(self)
        label_password.setText('Password:')
        label_password.move(20, 90)


        #Button
        self.button_ok = QPushButton('OK', self)
        self.button_ok.move(round(self.width*0.20), (self.height - 40))
        self.button_cancel = QPushButton('Cancel', self)
        self.button_cancel.move(round(self.width * 0.60), (self.height - 40))
        self.button_ok.clicked.connect(self.on_click_ok)
        self.button_cancel.clicked.connect(self.close)
        self.button_pdf_chooser = QPushButton('Pdf-Chooser', self)
        self.button_pdf_chooser.move(150, 120)
        self.button_pdf_chooser.clicked.connect(self.on_click_pdf_chooser)
        self.button_pdf_chooser.setStyleSheet("color: white;"
                        "background-color: grey;"
                        "selection-color: grey;"
                        "selection-background-color: white");

        self.create = QCheckBox('Create Lobby', self)
        self.create.move(35, 120)




    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def on_click_ok(self):
        if True:
            print('ConnectMessage: ' + self.textbox_lobby.text() + self.textbox_user.text() + self.textbox_password.text())

    def on_click_pdf_chooser(self):
        if self.create.isChecked():
            print("Open Pdf-Chooser")

class ExitLobbyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.title = 'ExitLobby'
        self.left = 100
        self.top = 100
        self.width = 250
        self.height = 100
        self.initUI()

        #Label
        label = QLabel(self)
        label.setText('Are you sure you want to leave Lobby? ') # + Lobbyname
        label.move(20, 20)

        # Button
        self.button_ok = QPushButton('OK', self)
        self.button_ok.move(round(self.width * 0.15), (self.height - 40))
        self.button_cancel = QPushButton('Cancel', self)
        self.button_cancel.move(round(self.width * 0.55), (self.height - 40))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #ex = CreateDialog()
    #ex.show()
    ey = ExitLobbyDialog()
    ey.show()
    sys.exit(app.exec_())
