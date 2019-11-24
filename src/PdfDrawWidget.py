import random
from typing import List, Tuple, Callable, Any

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QImage, QPaintEvent, QWheelEvent, QKeyEvent, QMouseEvent, QColor, QPen, QPolygon, \
    QBrush
from PyQt5.QtWidgets import QWidget, QScrollBar
from fitz import Document, Pixmap, fitz, Rect

from MessageTyp import ClientStatus


class PdfDrawWidget(QWidget):

    PAGESEPERATIONHEIGTH = 5

    horizontalScrollbar = None
    verticalScrollbar = None

    # Pdf rendering properties
    pdfVis: Document = None
    pageNum: int = 0
    zoom: float = 1

    __pdf_is_rendered = False
    __viewchanged = True
    __zoomed = True
    __pdfImages: List[Tuple[int, QImage]] = []  # List of Tuples where first index is the hightoffset
    __pageoffsets: List[int] = []
    __updatePagenum = True

    # Mouse and Keyboard vars
    __controlIsPressed = False
    __press_starting_pos: Tuple[float, float] = None
    __last_mousemove_event = None

    # Notifier
    mouse_move_notifier_send: Callable[[], Any] = None

    # Multi user
    external_client_dict: dict = None
    user_color_dict: dict = dict()
    multi_user_mode = False

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

    @property
    def yScrollValue(self):
        """Returns a y_scroll_value that is relative to the pdf"""
        return self.verticalScrollbar.value()/self.zoom

    @property
    def relativeMousePos(self) -> Tuple[float, float]:
        """Calculates a mouse position (x,y) relative to the pdf.
           x is 0 in the center of the pdf and increases for the right side
           y is 0 at the pdf top and ignores pageseperations"""
        if self.__last_mousemove_event is not None:
            yPos = (self.__last_mousemove_event.y() + self.verticalScrollbar.value()) / self.zoom
            xPos = (self.__last_mousemove_event.x() - self.width() / 2 + self.horizontalScrollbar.value()) / self.zoom
            return xPos, yPos
        else:
            return 0, 0

    def paintEvent(self, event: QPaintEvent):
        """All Drawing Actions are activated here"""
        self.__drawPDF(event)
        if self.multi_user_mode:
            self.__draw_coursers()


    def __draw_coursers(self):
        """Draws all Cursers of other users"""
        for key, val in self.external_client_dict.items():
            if key not in self.user_color_dict:
                self.user_color_dict[key] = QColor("#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]))

            x_global, y_global = val.mouse_pos
            x_global = x_global * self.zoom + self.width()/2 - self.horizontalScrollbar.value()
            y_global = y_global * self.zoom - self.verticalScrollbar.value()

            self.__draw_courser(self.user_color_dict[key], (x_global, y_global), val.user_name)


    def __draw_courser(self, color: QColor, point: Tuple[int, int], username: str):
        """Draws a single Cursor in a specified color"""
        self.painter.begin(self)
        pen = QPen()
        pen.setWidthF(1.7)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.painter.setPen(pen)
        self.painter.setBrush(QBrush(color, Qt.SolidPattern))
        points = QPolygon([
            QPoint(0, 0),
            QPoint(-10, 20),
            QPoint(0, 14),
            QPoint(10, 20)])

        points.translate(point[0], point[1])

        self.painter.drawPolygon(points)
        self.painter.end()

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
                    self.__zoomed = False

                prev_pagenum = next(num for num, height in enumerate(self.__pageoffsets, start=-1) if
                                    height >= self.verticalScrollbar.value())
                if self.__updatePagenum:
                    if self.pageNum != prev_pagenum:
                        new_scroll_value = self.__pageoffsets[self.pageNum] - self.__pageoffsets[prev_pagenum] + self.verticalScrollbar.value()
                        self.verticalScrollbar.setValue(new_scroll_value)
                        self.__updatePagenum = False
                else:
                    self.pageNum = prev_pagenum

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

                #Calculate Rectangle Coordinates for clipping
                clipx0 = (page.rect.width * self.zoom / 2 - self.width() / 2 + self.horizontalScrollbar.value()) / self.zoom \
                    if (page.rect.width * self.zoom / 2 - self.width() / 2 + self.horizontalScrollbar.value()) > 0 else 0
                clipy0 = (self.verticalScrollbar.value() - self.__pageoffsets[i]) / self.zoom \
                    if self.verticalScrollbar.value() >= self.__pageoffsets[i] else 0
                clipx1 = (page.rect.width * self.zoom / 2 + self.width() / 2 + self.horizontalScrollbar.value()) / self.zoom \
                    if (page.rect.width * self.zoom / 2 + self.width() / 2 + self.horizontalScrollbar.value()) / self.zoom < page.rect.width else page.rect.width
                clipy1 = (self.verticalScrollbar.value() + self.height() - self.__pageoffsets[i]) / self.zoom \
                    if self.verticalScrollbar.value() + self.height() - self.__pageoffsets[i] <= page.rect.height*self.zoom else page.rect.height

                # print(self.verticalScrollbar.value())
                pix: Pixmap = page.getPixmap(mat)#, clip=Rect(clipx0, clipy0, clipx1, clipy1))
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
                                       y + self.PAGESEPERATIONHEIGTH * i - self.verticalScrollbar.value(), img)
            self.painter.end()
            self.__pdf_is_rendered = True
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
        self.__press_starting_pos = (event.x(), event.y())

    def mouseMoveEvent(self, event: QMouseEvent):
        self.__last_mousemove_event = event
        if self.mouse_move_notifier_send is not None:
            self.mouse_move_notifier_send()
        if self.__press_starting_pos is not None:
            pass
            # Todo Draw Rectangle around all Textboxes

    def loadDocument(self, path: str):
        """loads a PDF"""
        self.pdfVis = fitz.Document(path)
        self.update()

    def updatePage(self, newPageNum: int=None, newPageDelta: int=None):
        """This Method jumps to the new page or by a given Delta
            if a newPageNum is given the delta will be applied to the new PageNum
            If the delta is not valid it won't be applied"""
        if newPageNum is not None:
            self.pageNum = newPageNum
        if newPageDelta is not None and self.pdfVis is not None:
            if self.pageNum - newPageDelta >= 0 and self.pageNum - newPageDelta < self.pdfVis.pageCount:
                self.pageNum += newPageDelta
        self.__updatePagenum = True
        self.update()


