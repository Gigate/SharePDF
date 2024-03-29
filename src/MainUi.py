import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QIntValidator
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QToolBar, QAction, qApp, \
    QFileDialog, QLineEdit, QSizePolicy


from src.PdfDrawWidget import PdfDrawWidget


class MainUI(QMainWindow):

    def __init__(self):
        
        super().__init__()

        verticalLayout = QVBoxLayout()
        horizontalLayout = QHBoxLayout()

        # Todo Add Draw function for MousePointers of others
        # The central Widget where all content is displayed
        centralwidget = QWidget(self)
        centralwidget.setObjectName("centralwidget")
        centralwidget.setLayout(verticalLayout)

        #Create the pdfWiget which Displays the PDF
        self.pdfWidget = PdfDrawWidget(centralwidget)

        #Set Layout Design
        horizontalLayout.addWidget(self.pdfWidget.verticalScrollbar)
        horizontalLayout.addWidget(self.pdfWidget)

        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addWidget(self.pdfWidget.horizontalScrollbar)

        self.toolbar: QToolBar = self.addToolBar("Toolbar1")
        self.fillToolbar()


        self.setCentralWidget(centralwidget)
        self.resize(800,600)
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


        self.intvalidator.setRange(0,0)
        self.pageNum = QLineEdit(self.toolbar)
        self.pageNum.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.pageNum.setValidator(self.intvalidator)
        self.pageNum.setFocusPolicy(Qt.ClickFocus)

        self.toolbar.addAction(exitAct)
        self.toolbar.addAction(openAct)
        self.toolbar.addWidget(self.pageNum)

    def keyPressEvent(self, event: QKeyEvent):
        """Connect all KeyPressEvents to the self.pdfWidget"""
        self.pdfWidget.keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        """Connect all KeyReleaseEvents to the self.pdfWidget"""
        self.pdfWidget.keyReleaseEvent(event)


    def getPath(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if fname[0]:
            self.pdfWidget.loadDocument(fname[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI()
    sys.exit(app.exec_())
