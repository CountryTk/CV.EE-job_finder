from urllib.request import urlopen
from bs4 import BeautifulSoup

from PyQt5.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QTabWidget, QDockWidget, QPlainTextEdit,  QApplication, \
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QGridLayout, QSizePolicy
from PyQt5.QtCore import QThread, Qt, pyqtSignal, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtTest import QTest
import sys
import os
import webbrowser

os.environ["PYTHONUNBUFFERED"] = "1"


class Label(QFrame):

    def __init__(self, text, url):

        super(Label, self).__init__()

        self.text = text
        self.url = url

        self.layout = QHBoxLayout()

        self.name = QLabel("<h3 color=#8E2DE2>" + self.text + "</h3>")
        self.clickable_url = QLabel("<font color=#396afc>" + self.url + "</font>")

        self.layout.addWidget(self.name)
        self.layout.addWidget(self.clickable_url)

        self.setLayout(self.layout)

        self.setStyleSheet("background-color: #f7797d")

    def mousePressEvent(self, QMouseEvent):
        webbrowser.open(self.url)

    def mouseMoveEvent(self, QMouseEvent):

        self.setCursor(Qt.ArrowCursor)


class Browser(QWebEngineView):

    def __init__(self, url):
        super().__init__()
        self.url = QUrl(url)

        self.load(QUrl(url))
        self.show()


class TextLabel(QFrame):

    def __init__(self, text):
        super().__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.layout = QHBoxLayout()
        self.text = text
        self.label = QLabel(str(self.text))
        self.removeButton = QPushButton("❌")

        self.removeButton.setFixedWidth(50)
        self.removeButton.setFixedHeight(50)

        self.layout.addWidget(self.label, Qt.AlignLeft)
        self.layout.addWidget(self.removeButton, Qt.AlignLeft)

        self.removeButton.clicked.connect(self.emitRemoveSignal)

        self.setStyleSheet("""
        
        QFrame {
        background-color: #f7797d;
        }
        
        QPushButton {
        background-color: transparent;
        }
        
        """)

        self.setLayout(self.layout)

    def emitRemoveSignal(self):

        self.close()


class Contents(QWidget):

    def __init__(self):

        super(Contents, self).__init__()

        self.content_widget = QWidget()
        self.scroll_area = QScrollArea()

        self.layout = QVBoxLayout(self.content_widget)

        self.scroll_area.setWidgetResizable(False)

        self.scroll_area.setWidget(self.content_widget)

        self.setLayout(self.layout)


class ModifiedLineEdit(QLineEdit):
    
    enterPressedSignal = pyqtSignal(bool)
    
    def __init__(self):
        
        super().__init__()

    def keyPressEvent(self, e):
        
        if e.key() == 16777220:
            self.enterPressedSignal.emit(True)
            self.setText("")
            return
        else:
            
            super().keyPressEvent(e)


class Config(QWidget):

    startSearching = pyqtSignal(list)
    otsiSignal = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__()

        self.layout = QVBoxLayout()
        self.valiku_layout = QHBoxLayout()

        self.valikud = []

        self.parent = parent

        self.title = QLabel("CV.ee töökohtade leidja")
        self.lisa_button = QPushButton("Lisa")
        self.mine_button = QPushButton("Otsi")
        self.vali = QLabel("Kirjuta siia töö märksõnad")
        self.vali_lineedit = ModifiedLineEdit()

        self.meme_widget = QWidget()
        self.meme_layout = QGridLayout(self.meme_widget)

        self.remove_all = QPushButton("Eemalda kõik")
        self.remove_all.setFixedWidth(125)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.meme_widget)

        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.title, Qt.AlignCenter)
        self.valiku_layout.addWidget(self.vali)
        self.valiku_layout.addWidget(self.vali_lineedit)
        self.valiku_layout.addWidget(self.lisa_button)
        self.valiku_layout.addWidget(self.mine_button)

        self.info_widget = QLabel()

        self.layout.addWidget(self.remove_all)
        self.layout.addWidget(self.scroll_area)
        self.layout.addLayout(self.valiku_layout)

        self.setLayout(self.layout)

        self.lisa_button.clicked.connect(self.lisa_sona)
        self.mine_button.clicked.connect(self.hakka_otsima)
        self.remove_all.clicked.connect(self.removing_all)

        self.vali_lineedit.enterPressedSignal.connect(self.lisa_sona)
        self.tracker = 0
        self.columns = 0

        self.vali_lineedit.setFocusPolicy(Qt.StrongFocus)
        self.vali_lineedit.setFocus()

    def removing_all(self):
        for i in reversed(range(self.meme_layout.count())):
            widgetToRemove = self.meme_layout.itemAt(i).widget()
            # remove it from the layout list
            self.meme_layout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)
        self.parent.parent.setFocus(Qt.ActiveWindowFocusReason)

    def hakka_otsima(self):

        self.valikud = []
        for i in range(self.meme_layout.count()):
            if self.meme_layout.itemAt(i).widget().text not in self.valikud:
                self.valikud.append(self.meme_layout.itemAt(i).widget().text)

        self.startSearching.emit(self.valikud)

    def lisa_voi_ei(self, sona):

        if sona not in self.valikud and len(sona) != 0:
            return True
        else:
            return False

    def lisa_sona(self):

        self.otsiSignal.emit(True)

        text = self.vali_lineedit.text()

        ok = TextLabel(str(text))
        if self.lisa_voi_ei(text):

            if self.meme_layout.count() % 5 != 0:

                self.tracker += 1
                print(self.tracker)
            else:

                self.columns += 1
                self.tracker = 0

            self.meme_layout.addWidget(ok, self.tracker, self.columns)


class Tabs(QWidget):

    def __init__(self, parent):

        super().__init__()

        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.parent = parent
        self.config = Config(self)
        self.peata = QPushButton("Peata otsing")

        self.config.otsiSignal.connect(lambda: self.peata.setText("Peata otsing"))

        self.tabs.addTab(self.config, "Seadista")

        self.layout.addWidget(self.tabs)

        self.layout.addWidget(self.peata)

        self.config.startSearching.connect(self.startThread)
        self.peata.clicked.connect(self.killthething)
        self.setLayout(self.layout)

    def killthething(self):

        try:
            self._thread.terminate()
            self.peata.setText("Peatatud...")
            print("Terminated")
        except AttributeError:
            print("nope")

    def startThread(self, keywords):

        self.contents = Contents()

        index = self.tabs.addTab(self.contents, "Leitud pakkumised")
        self.tabs.setCurrentIndex(index)
        self._thread = Scraper(keywords)

        print(keywords)

        if len(keywords) != 0:

            self._thread.start()

            self._thread.infoSignal.connect(self.showInfo)

    def showInfo(self, inf):

        # self.contents.layout.addWidget(Label(str(inf[0]), str(inf[1])))
        # self.contents.layout.addWidget(QLabel(str(inf)))
        webbrowser.open(inf[1])
        QTest.qWait(1000)


class Main(QMainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.meme = Tabs(self)

        self.setupUI()

        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

    def setupUI(self):

        self.setCentralWidget(self.meme)
    
    def keyPressEvent(self, e):
        if e.modifiers() == Qt.ControlModifier and e.key == Qt.Key_Q:
            os._exit(1)


class Scraper(QThread):

    infoSignal = pyqtSignal(list)

    def __init__(self, keywords):
        super(Scraper, self).__init__()

        self.keywords = keywords

    def run(self):

        i = 0
        interested_in = self.keywords
        i += 1

        print("Searching, current page number: {}".format(i))
        while True:
            url = "https://www.cv.ee/toopakkumised/harjumaa/infotehnoloogia?page={}".format(i)
            try:
                opened_url = urlopen(url).read()

                bs4_object = BeautifulSoup(opened_url, 'lxml')

                for div in bs4_object.find_all("div", class_="offer_primary"):
                    for a in div.find_all("a"):

                        found = "https://" + a['href'][2:]

                        try:
                            url_test = urlopen(found).read()

                            if "job-ad" in found:
                                newer_object = BeautifulSoup(url_test, "lxml")

                                content = newer_object.find("div", id="page-main-content").text

                                for i_need in interested_in:

                                    if i_need in content:
                                        self.infoSignal.emit([i_need, found])


                        except Exception as E:
                            pass

            except Exception as E:
                print("Breaking?")
                break


app = QApplication(sys.argv)
main = Main()
main.setWindowTitle("IT töö leidja")
main.show()
sys.exit(app.exec_())

