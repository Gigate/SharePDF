import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QIntValidator, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QToolBar, QAction, qApp, \
    QFileDialog, QLineEdit, QSizePolicy, QLabel

from CentraWidget import CentralWidget
from ConnectionHandler import ConnectionHandler
from PdfDrawWidget import PdfDrawWidget

from src.CreateDialog import CreateLobbyDialog, ExitLobbyDialog


class MainUI(QMainWindow):

    def __init__(self, version):
        self.version = version
        super().__init__()

        verticalLayout = QVBoxLayout()
        horizontalLayout = QHBoxLayout()

        # Todo Add Draw function for MousePointers of others
        # The central Widget where all content is displayed
        centralwidget = CentralWidget(self)
        centralwidget.setObjectName("centralwidget")
        centralwidget.setLayout(verticalLayout)

        # Create the pdfWiget which Displays the PDF
        self.pdfWidget = PdfDrawWidget(centralwidget)

        # Create Connectionhandler
        self.con_handler = ConnectionHandler(self.pdfWidget)

        # Set Layout Design
        horizontalLayout.addWidget(self.pdfWidget.verticalScrollbar)
        horizontalLayout.addWidget(self.pdfWidget)

        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addWidget(self.pdfWidget.horizontalScrollbar)

        self.toolbar: QToolBar = self.addToolBar("Toolbar1")
        self.fillToolbar()

        self.setCentralWidget(centralwidget)
        self.resize(800, 600)
        self.setWindowTitle('PdfViewer')
        self.show()

    intvalidator: QIntValidator = QIntValidator()
    pageNum: QLineEdit = None

    def fillToolbar(self):
        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)

        openAct = QAction('Open', self)
        openAct.setShortcut('Ctrl+O')
        openAct.triggered.connect(self.getPath)

        next_page = QAction('>', self)
        next_page.setShortcut(QKeySequence.MoveToNextPage)
        next_page_f = lambda: self.pdfWidget.updatePage(newPageDelta=1)
        next_page.triggered.connect(next_page_f)

        previous_page = QAction('<', self)
        previous_page.setShortcut(QKeySequence.MoveToPreviousPage)
        previous_page_f = lambda: self.pdfWidget.updatePage(newPageDelta=-1)
        previous_page.triggered.connect(previous_page_f)

        self.page_number = QLabel(self)
        self.page_number.setText('Page: 0')
        self.pdfWidget.call_page_num_changed = self.update_page_number

        joinAct = QAction('Join', self)
        joinAct.setShortcut('Ctrl+J')
        joinAct.triggered.connect(self.getJoin)

        exitLobbyAct = QAction('ExitJoin', self)
        exitLobbyAct.setShortcut('Ctrl+E')
        exitLobbyAct.triggered.connect(self.getLobbyExit)

        self.intvalidator.setRange(0, 0)
        # self.pageNum = QLineEdit(self.toolbar)
        # self.pageNum.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # self.pageNum.setValidator(self.intvalidator)
        # self.pageNum.setFocusPolicy(Qt.ClickFocus)

        self.toolbar.addAction(exitAct)
        self.toolbar.addAction(openAct)
        self.toolbar.addAction(previous_page)
        self.toolbar.addWidget(self.page_number)
        self.toolbar.addAction(next_page)

        # todo change page, show page number, join lobby, create lobby, show one mouse pointer, show names

    def update_page_number(self):
        self.page_number.setText(("Page: " + str(self.pdfWidget.pageNum)))
        self.toolbar.addAction(joinAct)
        self.toolbar.addAction(exitLobbyAct)
        self.toolbar.addWidget(self.pageNum)

    def keyPressEvent(self, event: QKeyEvent):
        """Connect all KeyPressEvents to the self.pdfWidget"""
        self.pdfWidget.keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        """Connect all KeyReleaseEvents to the self.pdfWidget"""
        self.pdfWidget.keyReleaseEvent(event)

    def getPath(self):
        print(self.version)
        if self.version:
            fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
            if fname[0]:
                self.pdfWidget.loadDocument(fname[0])
                print("connector method", self.con_handler.request_lobby_creation(
                    "localhost", 4454, "test3", "password", "Tim", fname[0]))
        else:
            print("connector method", self.con_handler.join_lobby(
                "localhost", 4454, "test3", "password", "Joshua"))
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if fname[0]:
            self.pdfWidget.loadDocument(fname[0])

    def getJoin(self):
        dialog = CreateLobbyDialog(self)
        dialog.show()


    def getLobbyExit(self):
        dialog = ExitLobbyDialog(self)
        dialog.show()


if __name__ == '__main__':
    app=QApplication(sys.argv)
    MainUI(sys.argv[1] == 'True')
    sys.exit(app.exec_())
