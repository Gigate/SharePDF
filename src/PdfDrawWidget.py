from typing import List, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QImage, QPaintEvent, QWheelEvent, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QScrollBar
from fitz import Document, Pixmap, fitz


class PdfDrawWidget(QWidget):
    horizontalScrollbar = None
    verticalScrollbar = None

    pdfVis: Document = None
    pageNum: int = 0
    zoom: float = 1

    __controlIsPressed = False

    __pressStart: Tuple[float, float] = None

    def __init__(self, parent: QWidget = None, painter: QPainter = QPainter()):
        super().__init__(parent)
        self.painter = painter
        self.horizontalScrollbar = QScrollBar(Qt.Horizontal)
        self.verticalScrollbar = QScrollBar(Qt.Vertical)
        self.horizontalScrollbar.setVisible(False)
        self.verticalScrollbar.setVisible(False)

        self.horizontalScrollbar.valueChanged.connect(lambda: self.update())
        self.verticalScrollbar.valueChanged.connect(lambda: self.update())
        self.setMouseTracking(True)

    def paintEvent(self, event: QPaintEvent):
        """All Drawing Actions are activated here"""
        self.__drawPDF(event)

    __viewchanged = True
    __zoomed = True
    __pdfImages: List[Tuple[int, QImage]] = []  # List of Tuples where first index is the hightoffset
    __pageoffsets: List[int] = []

    def __drawPDF(self, event: QPaintEvent):
        """Draws the Pdf centered onto the self Object as long as the self.pdfVis variable isn't None.
           self.verticalScrollbar &  self.horizontalScrollbar will be manipulated in range and visibility"""
        if self.pdfVis is not None:

            if self.__viewchanged:
                if self.__zoomed:
                    hightCount = 0
                    self.__pageoffsets = [0]
                    for page in self.pdfVis.pages():
                        hightCount += page.rect.height * self.zoom
                        self.__pageoffsets.append(hightCount)
                    hightCount -= self.height()
                    if self.height() < hightCount:
                        self.verticalScrollbar.setRange(0, hightCount)
                        self.verticalScrollbar.setVisible(True)
                    else:
                        self.verticalScrollbar.setVisible(False)
                        self.verticalScrollbar.setRange(0, 0)

            mat = fitz.Matrix(self.zoom, self.zoom)

            self.__pdfImages = []
            lowestVisablePage = next(i for i in range(len(self.__pageoffsets) - 1) if
                                     self.__pageoffsets[i + 1] >= self.verticalScrollbar.value())
            try:
                highestVisablePage = next(i for i in range(len(self.__pageoffsets) - 1) if self.__pageoffsets[
                    i + 1] >= self.verticalScrollbar.value() + self.height()) + 1
            except StopIteration:
                highestVisablePage = self.pdfVis.pageCount

            for falseI, page in enumerate(self.pdfVis.pages(lowestVisablePage, highestVisablePage)):
                i = falseI + lowestVisablePage
                clipx0 = (page.rect.width * self.zoom / 2 - self.width() / 2 + self.horizontalScrollbar.value()) \
                    if (
                               page.rect.width * self.zoom / 2 - self.width() / 2 + self.horizontalScrollbar.value()) > 0 else 0
                clipy0 = (self.verticalScrollbar.value() - self.__pageoffsets[i]) / self.zoom \
                    if self.verticalScrollbar.value() >= self.__pageoffsets[i] else 0
                # clipx1 =
                # clipy1 =
                print(clipy0, clipx0)
                # print(self.verticalScrollbar.value())
                pix: Pixmap = page.getPixmap(mat)  # , clip=Rect(0,0,110,110))
                fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
                self.__pdfImages.append(
                    (self.__pageoffsets[i], QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)))

            if self.__pdfImages[0][1].width() > self.width():
                self.horizontalScrollbar.setRange(self.width() - self.__pdfImages[0][1].width(),
                                                  self.__pdfImages[0][1].width() - self.width())
                self.horizontalScrollbar.setVisible(True)
            else:
                self.horizontalScrollbar.setVisible(False)
                self.horizontalScrollbar.setRange(0, 0)

                self.__viewchanged = False

            self.painter.begin(self)
            for i, (y, img) in enumerate(self.__pdfImages):
                self.painter.drawImage(self.painter.viewport().width() / 2 - img.width() / 2
                                       - self.horizontalScrollbar.value(),
                                       y + 5 * i - self.verticalScrollbar.value(), img)
            self.painter.end()
        else:
            pass

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)

    def wheelEvent(self, event: QWheelEvent):
        if self.__controlIsPressed:
            if self.zoom + 0.005 * event.angleDelta().y() > 0:
                self.zoom += 0.005 * event.angleDelta().y()
            else:
                self.zoom = 0.1
            self.__zoomed = True
        else:
            self.verticalScrollbar.setValue(self.verticalScrollbar.value() - event.angleDelta().y())
        self.__viewchanged = True
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Control:
            self.__controlIsPressed = True

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Control:
            self.__controlIsPressed = False

    def mousePressEvent(self, event: QMouseEvent):
        self.__pressStart = (event.x(), event.y())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.__pressStart is not None:
            pass
            # Todo Draw Rectangle around all Textboxes

    def loadDocument(self, path: str):
        self.pdfVis = fitz.Document(path)
        self.update()
