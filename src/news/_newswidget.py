import logging
import webbrowser

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import QUrl

import util
from config import Settings
from util.qt import ExternalLinkPage

from .newsitem import NewsItem, NewsItemDelegate
from .newsmanager import NewsManager

logger = logging.getLogger(__name__)


class Hider(QtCore.QObject):
    """
    Hides a widget by blocking its paint event. This is useful if a
    widget is in a layout that you do not want to change when the
    widget is hidden.
    """

    def __init__(self, parent=None):
        super(Hider, self).__init__(parent)

    def eventFilter(self, obj, ev):
        return ev.type() == QtCore.QEvent.Paint

    def hide(self, widget):
        widget.installEventFilter(self)
        widget.update()

    def unhide(self, widget):
        widget.removeEventFilter(self)
        widget.update()

    def hideWidget(self, sender):
        if sender.isWidgetType():
            self.hide(sender)


FormClass, BaseClass = util.THEME.loadUiType("news/news.ui")


class NewsWidget(FormClass, BaseClass):
    CSS = util.THEME.readstylesheet('news/news_webview.css')

    HTML = str(util.THEME.readfile('news/news_webview_frame.html'))

    def __init__(self, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)


        # self.webview = QtWebEngineWidgets.QWebEngineView()
        # self.webpage = QtWebEngineWidgets.QWebEnginePage()
        # self.webpage.profile().setHttpUserAgent("FAF Client")
        # self.hider2 = Hider()
        # self.hider2.hide(self.newsWebView2)

        # self.webpage.setUrl(
        #     QtCore.QUrl("https://faforever.com/newshub"),
        # )
        # self.webview.setPage(self.webpage)

        self.setupUi(self)

        self.newsWebView2.loadFinished.connect(self.newsWebView2.show)
        self.webpage = QtWebEngineWidgets.QWebEnginePage()
        #self.newsWebView2.load(QUrl("https://faforever.com/newshub/"))
        #self.newsWebView2.setPage(ExternalLinkPage(self))
        self.webpage.setUrl(
            QtCore.QUrl("https://faforever.com/newshub/"),
        )
        self.newsWebView2.loadFinished.connect(self.newsWebView2.show)
        #self.newsWebView2.setPage(ExternalLinkPage(self))
        self.newsWebView2.setPage(self.webpage)


    def addNews(self, newsPost):{}

    # QtWebEngine has no user CSS support yet, so let's just prepend it to the
    # HTML
    def _injectCSS(self, body, link, img):{}

    def updateNews(self):{}

    def itemChanged(self, current, previous): {}

    def linkClicked(self, url):{}

    def loadFinished(self, ok):{}

    def showAll(self):{}

    def showEditToolTip(self):{}

    def showSettings(self):{}
    def updateNewsFilter(self, text=False):{}

    def updateLabel(self, number):{}
