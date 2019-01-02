#!/usr/bin/python3
# -- coding: utf-8 --
from __future__ import print_function

from PyQt5.QtWidgets import (QPlainTextEdit, QWidget, QVBoxLayout, QApplication, QFileDialog, QMessageBox, QLabel, QCompleter, 
                                                    QHBoxLayout, QTextEdit, QToolBar, QComboBox, QAction, QLineEdit, QDialog, QPushButton, 
                                                     QToolButton, QMenu, QMainWindow, QInputDialog, QColorDialog, QStatusBar, QSystemTrayIcon)
from PyQt5.QtGui import (QIcon, QPainter, QTextFormat, QColor, QTextCursor, QKeySequence, QClipboard, QTextDocument, 
                                        QPixmap, QStandardItemModel, QStandardItem, QCursor)
from PyQt5.QtCore import (Qt, QVariant, QRect, QDir, QFile, QFileInfo, QTextStream, QSettings, QTranslator, QLocale, 
                                            QProcess, QPoint, QSize, QCoreApplication, QStringListModel, QLibraryInfo)
from PyQt5 import QtPrintSupport
from sys import argv
import inspect
from syntax_py import *
import os
import sys
import re
import customcompleter_rc

lineBarColor = QColor("#d3d7cf")
lineHighlightColor  = QColor("#fce94f")
tab = chr(9)
eof = "\n"
iconsize = QSize(16, 16)

    #####################################################################
class TextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)

        self.installEventFilter(self)
        self._completer = None

    def setCompleter(self, c):
        if self._completer is not None:
            self._completer.activated.disconnect()

        self._completer = c
#        c.popup().verticalScrollBar().hide()
        c.popup().setStyleSheet("background-color: #555753; color: #eeeeec; font-size: 8pt; selection-background-color: #4e9a06;")

        c.setWidget(self)
        c.setCompletionMode(QCompleter.PopupCompletion)
        c.activated.connect(self.insertCompletion)

    def completer(self):
        return self._completer

    def insertCompletion(self, completion):
        if self._completer.widget() is not self:
            return

        tc = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)

        return tc.selectedText()

    def focusInEvent(self, e):
        if self._completer is not None:
            self._completer.setWidget(self)

        super(TextEdit, self).focusInEvent(e)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Tab:
            self.textCursor().insertText("    ")
            return
        if self._completer is not None and self._completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget.
            if e.key() in (Qt.Key_Enter, Qt.Key_Return):
                e.ignore()
                # Let the completer do default behavior.
                return

        isShortcut = ((e.modifiers() & Qt.ControlModifier) != 0 and e.key() == Qt.Key_Escape)
        if self._completer is None or not isShortcut:
            # Do not process the shortcut when we have a completer.
            super(TextEdit, self).keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if self._completer is None or (ctrlOrShift and len(e.text()) == 0):
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        hasModifier = (e.modifiers() != Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()

        if not isShortcut and (hasModifier or len(e.text()) == 0 or len(completionPrefix) < 2 or e.text()[-1] in eow):
            self._completer.popup().hide()
            return

        if completionPrefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completionPrefix)
            self._completer.popup().setCurrentIndex(
                    self._completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)
    ####################################################################

class NumberBar(QWidget):
    def __init__(self, parent = None):
        super(NumberBar, self).__init__(parent)
        self.editor = parent
        layout = QVBoxLayout()
        self.editor.blockCountChanged.connect(self.update_width)
        self.editor.updateRequest.connect(self.update_on_scroll)
        self.update_width('1')

    def update_on_scroll(self, rect, scroll):
        if self.isVisible():
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update()

    def update_width(self, string):
        width = self.fontMetrics().width(str(string)) + 8
        if self.width() != width:
            self.setFixedWidth(width)

    def paintEvent(self, event):
        if self.isVisible():
            block = self.editor.firstVisibleBlock()
            height = self.fontMetrics().height()
            number = block.blockNumber()
            painter = QPainter(self)
            painter.fillRect(event.rect(), lineBarColor)
            painter.drawRect(0, 0, event.rect().width() - 1, event.rect().height() - 1)
            font = painter.font()

            current_block = self.editor.textCursor().block().blockNumber() + 1

            condition = True
            while block.isValid() and condition:
                block_geometry = self.editor.blockBoundingGeometry(block)
                offset = self.editor.contentOffset()
                block_top = block_geometry.translated(offset).top()
                number += 1

                rect = QRect(0, block_top + 2, self.width() - 5, height)

                if number == current_block:
                    font.setBold(True)
                else:
                    font.setBold(False)

                painter.setFont(font)
                painter.drawText(rect, Qt.AlignRight, '%i'%number)

                if block_top > event.rect().bottom():
                    condition = False

                block = block.next()

            painter.end()

class myEditor(QMainWindow):
    def __init__(self, parent = None):
        super(myEditor, self).__init__(parent)

        self.root = QFileInfo.path(QFileInfo(QCoreApplication.arguments()[0]))
        self.wordList = []
        print("self.root is: ", self.root)
        self.appfolder = self.root
        self.statusBar().showMessage(self.appfolder)
        self.lineLabel = QLabel("line")
        self.statusBar().addPermanentWidget(self.lineLabel)
        self.MaxRecentFiles = 15
        self.windowList = []
        self.recentFileActs = []
        self.settings = QSettings("PyEdit", "PyEdit")
        self.dirpath = QDir.homePath() + "/Dokumente/python_files/"
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(QIcon.fromTheme("applications-python"))


        # Editor Widget ...
        self.editor = TextEdit()

        self.completer = QCompleter(self)
        self.completer.setModel(self.modelFromFile(self.root + '/resources/wordlist.txt'))
        self.completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWrapAround(False)
        self.completer.setCompletionRole(Qt.EditRole)
        self.editor.setCompleter(self.completer)

        self.editor.setStyleSheet(stylesheet2(self))
#        self.editor.setTabStopWidth(20)
        self.editor.cursorPositionChanged.connect(self.cursorPositionChanged)
        self.extra_selections = []
        self.mainText = "#!/usr/bin/python3\n# -*- coding: utf-8 -*-\n"
        self.fname = ""
        self.filename = ""
        self.mypython = "2"
        self.mylabel = QTextEdit()
        self.mylabel.setFixedHeight(90)
        self.mylabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # Line Numbers ...
        self.numbers = NumberBar(self.editor)
        self.createActions()
        # Syntax Highlighter ...
        self.highlighter = Highlighter(self.editor.document())
        # Laying out...
        layoutH = QHBoxLayout()
        layoutH.setSpacing(1.5)
        layoutH.addWidget(self.numbers)
        layoutH.addWidget(self.editor)
        ### systray
        self.createTrayIcon()
        self.trayIcon.show()
        ### statusbar
        self.statusBar()
        self.statusBar().setStyleSheet(stylesheet2(self))
        self.statusBar().showMessage('Welcome')
        ### begin toolbar
        tb = self.addToolBar("File")
        tb.setStyleSheet(stylesheet2(self))
        tb.setContextMenuPolicy(Qt.PreventContextMenu)
        tb.setIconSize(QSize(iconsize))
        tb.setMovable(True)
        tb.setAllowedAreas(Qt.AllToolBarAreas)
        tb.setFloatable(True)
       
        ### file buttons
        self.newAct = QAction("&New", self, shortcut=QKeySequence.New,
                statusTip="new file", triggered=self.newFile)
        self.newAct.setIcon(QIcon.fromTheme(self.root + "/icons/new24"))
        tb.addAction(self.newAct)
        
        self.openAct = QAction("&Open", self, shortcut=QKeySequence.Open,
                statusTip="open file", triggered=self.openFile)
        self.openAct.setIcon(QIcon.fromTheme(self.root + "/icons/open24"))
        tb.addAction(self.openAct)

        self.saveAct = QAction("&Save", self, shortcut=QKeySequence.Save,
                statusTip="save file", triggered=self.fileSave)
        self.saveAct.setIcon(QIcon.fromTheme(self.root + "/icons/floppy24"))
        tb.addAction(self.saveAct)
        
        self.saveAsAct = QAction("&Save as ...", self, shortcut=QKeySequence.SaveAs,
                statusTip="save file as ...", triggered=self.fileSaveAs)
        self.saveAsAct.setIcon(QIcon.fromTheme(self.root + "/icons/floppy25"))
        tb.addAction(self.saveAsAct)

        self.jumpToAct = QAction("go to Definition", self, shortcut="F12",
                                     statusTip="go to def", triggered=self.gotoBookmarkFromMenu)
        self.jumpToAct.setIcon(QIcon.fromTheme("go-next"))
        
        ### comment buttons       
        tb.addSeparator()           
        self.commentAct = QAction("#comment Line", self, shortcut="F2",
                statusTip="comment Line (F2)", triggered=self.commentLine)
        self.commentAct.setIcon(QIcon.fromTheme(self.root + "/icons/comment"))
        tb.addAction(self.commentAct)
                         
        self.uncommentAct = QAction("uncomment Line", self, shortcut="F3",
                statusTip="uncomment Line (F3)", triggered=self.uncommentLine)
        self.uncommentAct.setIcon(QIcon.fromTheme(self.root + "/icons/uncomment"))
        tb.addAction(self.uncommentAct)  
        
        self.commentBlockAct = QAction("comment Block", self, shortcut="F6",
                statusTip="comment selected block (F6)", triggered=self.commentBlock)
        self.commentBlockAct.setIcon(QIcon.fromTheme(self.root + "/icons/commentBlock"))
        tb.addAction(self.commentBlockAct)  
        
        self.uncommentBlockAct = QAction("uncomment Block (F7)", self, shortcut="F7",
                statusTip="uncomment selected block (F7)", triggered=self.uncommentBlock)
        self.uncommentBlockAct.setIcon(QIcon.fromTheme(self.root + "/icons/uncommentBlock"))
        tb.addAction(self.uncommentBlockAct)
        ### color chooser
        tb.addSeparator()
        tb.addAction(QIcon.fromTheme(self.root + "/icons/color1"),"insert QColor", self.insertColor)
        tb.addSeparator()
        tb.addAction(QIcon.fromTheme("preferences-color"),"change Color", self.changeColor)    
        ###insert templates
        tb.addSeparator()
        self.templates = QComboBox()
        self.templates.setStyleSheet(stylesheet2(self))
        self.templates.setFixedWidth(120)
        self.templates.setToolTip("insert template")
        self.templates.activated[str].connect(self.insertTemplate)
        tb.addWidget(self.templates)
        ### path python buttons      
        tb.addSeparator()   
        self.py2Act = QAction("run in Python 2 (F4)", self, shortcut="F4",
                statusTip="run in Python 2 (F4)", triggered=self.runPy2)
        self.py2Act.setIcon(QIcon.fromTheme("applications-python"))
        tb.addAction(self.py2Act)                               
        self.py3Act = QAction("run in Python 3.6 (F6)", self, shortcut="F6",
                statusTip="run in Python 3 (F5)", triggered=self.runPy3)
        self.py3Act.setIcon(QIcon.fromTheme(self.root + "/icons/python3"))
        tb.addAction(self.py3Act)
        tb.addSeparator()
        tb.addAction(QIcon.fromTheme("edit-clear"),"clear Output Label", self.clearLabel)
        tb.addSeparator()
        ### print preview
        self.printPreviewAct = QAction("Print Preview", self, shortcut="Ctrl+Shift+P",
                statusTip="Preview Document", triggered=self.handlePrintPreview)
        self.printPreviewAct.setIcon(QIcon.fromTheme("document-print-preview"))
        tb.addAction(self.printPreviewAct)
        ### print
        self.printAct = QAction("Print", self, shortcut=QKeySequence.Print,
                statusTip="Print Document", triggered=self.handlePrint)
        self.printAct.setIcon(QIcon.fromTheme("document-print"))
        tb.addAction(self.printAct) 
        ### about buttons
        tb.addSeparator()
        tb.addAction(QIcon.fromTheme(self.root + "/icons/info2"),"&About PyEdit", self.about)
        tb.addSeparator()
        ### exit button
        self.exitAct = QAction("exit", self, shortcut=QKeySequence.Quit,
                statusTip="Exit", triggered=self.handleQuit)
        self.exitAct.setIcon(QIcon.fromTheme(self.root + "/icons/quit"))
        tb.addAction(self.exitAct)     
        ### end toolbar
        self.indentAct = QAction(QIcon.fromTheme(self.root + "/icons/format-indent-more"), "indent more", self, triggered = self.indentLine, shortcut = "F8")
        self.indentLessAct = QAction(QIcon.fromTheme(self.root + "/icons/format-indent-less"), "indent less", self, triggered = self.indentLessLine, shortcut = "F9")
        ### find / replace toolbar
        self.addToolBarBreak()
        tbf = self.addToolBar("Find")
        tbf.setStyleSheet(stylesheet2(self))
        tbf.setContextMenuPolicy(Qt.PreventContextMenu)
        tbf.setIconSize(QSize(iconsize))
        self.findfield = QLineEdit()
        self.findfield.setStyleSheet(stylesheet2(self))
        self.findfield.addAction(QIcon.fromTheme("edit-find"), QLineEdit.LeadingPosition)
        self.findfield.setClearButtonEnabled(True)
        self.findfield.setFixedWidth(150)
        self.findfield.setPlaceholderText("find")
        self.findfield.setToolTip("press RETURN to find")
        self.findfield.setText("")
        ft = self.findfield.text()
        self.findfield.returnPressed.connect(self.findText)
        tbf.addWidget(self.findfield)
        self.replacefield = QLineEdit()
        self.replacefield.setStyleSheet(stylesheet2(self))
        self.replacefield.addAction(QIcon.fromTheme("edit-find-and-replace"), QLineEdit.LeadingPosition)
        self.replacefield.setClearButtonEnabled(True)
        self.replacefield.setFixedWidth(150)
        self.replacefield.setPlaceholderText("replace with")
        self.replacefield.setToolTip("press RETURN to replace the first")
        self.replacefield.returnPressed.connect(self.replaceOne)
        tbf.addSeparator() 
        tbf.addWidget(self.replacefield)
        tbf.addSeparator()
        
        self.repAllAct = QPushButton("replace all") 
        self.repAllAct.setFixedWidth(100)
        self.repAllAct.setStyleSheet(stylesheet2(self))
        self.repAllAct.setIcon(QIcon.fromTheme("gtk-find-and-replace"))
        self.repAllAct.setStatusTip("replace all")
        self.repAllAct.clicked.connect(self.replaceAll)
        tbf.addWidget(self.repAllAct)
        tbf.addSeparator()
        tbf.addAction(self.indentAct)
        tbf.addAction(self.indentLessAct)
        tbf.addSeparator()
        self.gotofield = QLineEdit()
        self.gotofield.setStyleSheet(stylesheet2(self))
        self.gotofield.addAction(QIcon.fromTheme("next"), QLineEdit.LeadingPosition)
        self.gotofield.setClearButtonEnabled(True)
        self.gotofield.setFixedWidth(120)
        self.gotofield.setPlaceholderText("go to line")
        self.gotofield.setToolTip("press RETURN to go to line")
        self.gotofield.returnPressed.connect(self.gotoLine)
        tbf.addWidget(self.gotofield)
        
        tbf.addSeparator() 
        self.bookmarks = QComboBox()
        self.bookmarks.setStyleSheet(stylesheet2(self))
        self.bookmarks.setFixedWidth(280)
        self.bookmarks.setToolTip("go to bookmark")
        self.bookmarks.activated[str].connect(self.gotoBookmark)
        tbf.addWidget(self.bookmarks)

        self.bookAct = QAction("add Bookmark", self,
                statusTip="add Bookmark", triggered=self.addBookmark)
        self.bookAct.setIcon(QIcon.fromTheme("previous"))
        tbf.addAction(self.bookAct)
        
        tbf.addSeparator()
        self.bookrefresh = QAction("update Bookmarks", self,
                statusTip="update Bookmarks", triggered=self.findBookmarks)
        self.bookrefresh.setIcon(QIcon.fromTheme("view-refresh"))
        tbf.addAction(self.bookrefresh)
        tbf.addAction(QAction(QIcon.fromTheme("document-properties"), "check && reindent Text", self, triggered=self.reindentText))
        
        layoutV = QVBoxLayout()
        
        bar=self.menuBar()
        bar.setStyleSheet(stylesheet2(self))
        self.filemenu=bar.addMenu("File")
        self.filemenu.setStyleSheet(stylesheet2(self))
        self.separatorAct = self.filemenu.addSeparator()
        self.filemenu.addAction(self.newAct)
        self.filemenu.addAction(self.openAct)
        self.filemenu.addAction(self.saveAct)
        self.filemenu.addAction(self.saveAsAct)
        self.filemenu.addSeparator()
        for i in range(self.MaxRecentFiles):
            self.filemenu.addAction(self.recentFileActs[i])
        self.updateRecentFileActions()
        self.filemenu.addSeparator()
        self.clearRecentAct = QAction("clear Recent Files List", self, triggered=self.clearRecentFiles)
        self.clearRecentAct.setIcon(QIcon.fromTheme("edit-clear"))
        self.filemenu.addAction(self.clearRecentAct)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.exitAct)
        
        editmenu = bar.addMenu("Edit")
        editmenu.setStyleSheet(stylesheet2(self))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-undo'), "Undo", self, triggered = self.editor.undo, shortcut = "Ctrl+u"))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-redo'), "Redo", self, triggered = self.editor.redo, shortcut = "Shift+Ctrl+u"))
        editmenu.addSeparator()
        editmenu.addAction(QAction(QIcon.fromTheme('edit-copy'), "Copy", self, triggered = self.editor.copy, shortcut = "Ctrl+c"))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-cut'), "Cut", self, triggered = self.editor.cut, shortcut = "Ctrl+x"))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-paste'), "Paste", self, triggered = self.editor.paste, shortcut = "Ctrl+v"))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-delete'), "Delete", self, triggered = self.editor.cut, shortcut = "Del"))
        editmenu.addSeparator()
        editmenu.addAction(QAction(QIcon.fromTheme('edit-select-all'), "Select All", self, triggered = self.editor.selectAll, shortcut = "Ctrl+a"))
        editmenu.addSeparator()
        editmenu.addAction(self.commentAct)
        editmenu.addAction(self.uncommentAct)
        editmenu.addSeparator()
        editmenu.addAction(self.commentBlockAct)
        editmenu.addAction(self.uncommentBlockAct)
        editmenu.addSeparator()
        editmenu.addAction(self.py2Act)
        editmenu.addAction(self.py3Act)
        editmenu.addSeparator()
        editmenu.addAction(self.jumpToAct)
        editmenu.addSeparator()
        editmenu.addAction(self.indentAct)
        editmenu.addAction(self.indentLessAct)

        layoutV.addLayout(layoutH)
        self.mylabel.setMinimumHeight(28)
        self.mylabel.setStyleSheet(stylesheet2(self))
        layoutV.addWidget(self.mylabel)
        ### main window
        mq = QWidget(self)
        mq.setLayout(layoutV)
        self.setCentralWidget(mq)
        
        # Event Filter ...
#        self.installEventFilter(self)
        self.editor.setFocus()
        self.cursor = QTextCursor()
        self.editor.setTextCursor(self.cursor)
        self.editor.setPlainText(self.mainText)
        self.editor.moveCursor(self.cursor.End)
        self.editor.document().modificationChanged.connect(self.setWindowModified)
        
        # Brackets ExtraSelection ...
        self.left_selected_bracket  = QTextEdit.ExtraSelection()
        self.right_selected_bracket = QTextEdit.ExtraSelection()
        
        ### shell settings
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(lambda: self.mylabel.append("starting shell"))
        self.process.finished.connect(lambda: self.mylabel.append("shell ended"))

        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.contextMenuRequested)
        
        self.loadTemplates()   
        self.readSettings()
        self.statusBar().showMessage("self.root is: " + self.root, 0)

    def keyPressEvent(self, event):
        if  self.editor.hasFocus():
            if event.key() == Qt.Key_F10:
                self.findNextWord()

    def cursorPositionChanged(self):
        line = self.editor.textCursor().blockNumber() + 1
        pos = self.editor.textCursor().positionInBlock()
        self.lineLabel.setText("line " + str(line) + " - position " + str(pos))
        
    def textColor(self):
        col = QColorDialog.getColor(QColor("#" + self.editor.textCursor().selectedText()), self)
        self.pix.fill(col)
        if not col.isValid():
            return
        else:
            colorname = 'QColor("' + col.name() + '")'
            self.editor.textCursor().insertText(colorname)
            self.pix.fill(col)
        
    def loadTemplates(self):
        folder = self.appfolder + "/templates"
        if QDir().exists(folder):
            self.currentDir = QDir(folder)
            count = self.currentDir.count()
            fileName = "*"
            files = self.currentDir.entryList([fileName],
                    QDir.Files | QDir.NoSymLinks)

            for i in range(count - 2):
                file = (files[i])
                if file.endswith(".txt"):
                    self.templates.addItem(file.replace(self.appfolder + "/templates", "").replace(".txt", ""))
        
    def Test(self):
        self.editor.selectAll()
        
    def reindentText(self):
        if self.editor.toPlainText() == "" or self.editor.toPlainText() == self.mainText:
            self.statusBar().showMessage("no code to reindent")
        else:
            self.editor.selectAll()
            tab = "\t"
            oldtext = self.editor.textCursor().selectedText()
            newtext = oldtext.replace(tab, "    ")
            self.editor.textCursor().insertText(newtext)    
            self.statusBar().showMessage("reindented")

    def insertColor(self):
        col = QColorDialog.getColor(QColor("#000000"), self)
        if not col.isValid():
            return
        else:
            colorname = 'QColor("' + col.name() + '")'
            self.editor.textCursor().insertText(colorname)
            
    def changeColor(self):
        if not self.editor.textCursor().selectedText() == "":
            col = QColorDialog.getColor(QColor("#" + self.editor.textCursor().selectedText()), self)
            if not col.isValid():
                return
            else:
                colorname = col.name()
                self.editor.textCursor().insertText(colorname.replace("#", ""))
        else:
            col = QColorDialog.getColor(QColor("black"), self)
            if not col.isValid():
                return
            else:
                colorname = col.name()
                self.editor.textCursor().insertText(colorname)

    ### QPlainTextEdit contextMenu
    def contextMenuRequested(self,point):
        cmenu = QMenu()
        cmenu = self.editor.createStandardContextMenu()
        cmenu.addSeparator()
        cmenu.addAction(self.jumpToAct)
        cmenu.addSeparator()
        if not self.editor.textCursor().selectedText() == "":
            cmenu.addAction(QIcon.fromTheme("gtk-find-and-replace"),"replace all occurrences with", self.replaceThis)
            cmenu.addSeparator()
        cmenu.addAction(QIcon.fromTheme("zeal"),"show help with 'zeal'", self.showZeal)
        cmenu.addAction(QIcon.fromTheme("gtk-find-"),"find this (F10)", self.findNextWord)
        cmenu.addSeparator()
        cmenu.addAction(self.py2Act)
        cmenu.addAction(self.py3Act)
        cmenu.addSeparator()
        cmenu.addAction(self.commentAct)
        cmenu.addAction(self.uncommentAct)
        cmenu.addSeparator()
        if not self.editor.textCursor().selectedText() == "":
            cmenu.addAction(self.commentBlockAct)
            cmenu.addAction(self.uncommentBlockAct)
            cmenu.addSeparator()
            cmenu.addAction(self.indentAct)
            cmenu.addAction(self.indentLessAct)       
        cmenu.addSeparator()
        cmenu.addAction(QIcon.fromTheme("preferences-color"),"insert QColor", self.insertColor)

        cmenu.addSeparator()
        cmenu.addAction(QIcon.fromTheme("preferences-color"),"change Color", self.changeColor)
        cmenu.exec_(self.editor.mapToGlobal(point))    
        
    def replaceThis(self):
        rtext = self.editor.textCursor().selectedText()
        text = QInputDialog.getText(self, "replace with","replace '" + rtext + "' with:", QLineEdit.Normal, "")
        oldtext = self.editor.document().toPlainText()
        if not (text[0] == ""):
            newtext = oldtext.replace(rtext, text[0])
            self.editor.setPlainText(newtext)
            self.setModified(True)

    def showZeal(self):
        if self.editor.textCursor().selectedText() == "":
            tc = self.editor.textCursor()
            tc.select(QTextCursor.WordUnderCursor)
            rtext = tc.selectedText()
            print(rtext)
#            self.editor.moveCursor(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
#            self.editor.moveCursor(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
        else:
            rtext = self.editor.textCursor().selectedText()
        cmd = "zeal " + str(rtext)
        QProcess().startDetached(cmd)

    def findNextWord(self):
        if self.editor.textCursor().selectedText() == "":
            self.editor.moveCursor(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
            self.editor.moveCursor(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
        rtext = self.editor.textCursor().selectedText()
        self.findfield.setText(rtext)
        self.findText()

        
    def indentLine(self):
        if not self.editor.textCursor().selectedText() == "":
            newline = u"\u2029"
            list = []
            ot = self.editor.textCursor().selectedText()
            theList  = ot.splitlines()
            linecount = ot.count(newline)
            for i in range(linecount + 1):
                list.insert(i, "    " + theList[i])
            self.editor.textCursor().insertText(newline.join(list))
            self.setModified(True)   
#            self.editor.find(ot)
            self.statusBar().showMessage("tabs indented")
        
    def indentLessLine(self):
        if not self.editor.textCursor().selectedText() == "":
            newline = u"\u2029"
            list = []
            ot = self.editor.textCursor().selectedText()
            theList  = ot.splitlines()
            linecount = ot.count(newline)
            for i in range(linecount + 1):
                list.insert(i, (theList[i]).replace("    ", "", 1))
            self.editor.textCursor().insertText(newline.join(list))
            self.setModified(True)    
#            self.editor.find(ot)
            self.statusBar().showMessage("tabs deleted")
        
    def dataReady(self):
        out = ""
        try:
            out = str(self.process.readAll(), encoding = 'utf8').rstrip()
        except TypeError:
            self.msgbox("Error", str(self.process.readAll(), encoding = 'utf8'))
            out = str(self.process.readAll()).rstrip()
        self.mylabel.moveCursor(self.cursor.Start)
        self.mylabel.append(out)    
        if self.mylabel.find("line", QTextDocument.FindWholeWords):
            t = self.mylabel.toPlainText().partition("line")[2].partition("\n")[0].lstrip()
            if t.find(",", 0):
                tr = t.partition(",")[0]
            else:
                tr = t.lstrip()
            self.gotoErrorLine(tr)
        else:
            return
        self.mylabel.moveCursor(self.cursor.End)
        self.mylabel.ensureCursorVisible()
        
    def createActions(self):
        for i in range(self.MaxRecentFiles):
            self.recentFileActs.append(
                   QAction(self, visible=False,
                            triggered=self.openRecentFile))
            
    def addBookmark(self):
        linenumber = self.getLineNumber()
        linetext = self.editor.textCursor().block().text().strip()
        self.bookmarks.addItem(linetext, linenumber)
        
    def getLineNumber(self):
        self.editor.moveCursor(self.cursor.StartOfLine)
        linenumber = self.editor.textCursor().blockNumber() + 1
        return linenumber
            
    def gotoLine(self):
        ln = int(self.gotofield.text())
        linecursor = QTextCursor(self.editor.document().findBlockByLineNumber(ln-1))
        self.editor.moveCursor(QTextCursor.End)
        self.editor.setTextCursor(linecursor)
        
    def gotoErrorLine(self, ln):
        if ln.isalnum:
            t = int(ln)
            if t != 0:
                linecursor = QTextCursor(self.editor.document().findBlockByLineNumber(t-1))
                self.editor.moveCursor(QTextCursor.End)
                self.editor.setTextCursor(linecursor)
                self.editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            else:
                return
        
    def gotoBookmark(self):
        if self.editor.find(self.bookmarks.itemText(self.bookmarks.currentIndex())):
            pass
        else:
            self.editor.moveCursor(QTextCursor.Start)
            self.editor.find(self.bookmarks.itemText(self.bookmarks.currentIndex()))

        self.editor.centerCursor()
        self.editor.moveCursor(self.cursor.StartOfLine, self.cursor.MoveAnchor)
        
    def gotoBookmarkFromMenu(self):
        if self.editor.textCursor().selectedText() == "":
            tc = self.editor.textCursor()
            tc.select(QTextCursor.WordUnderCursor)
            rtext = tc.selectedText()
        else:
            rtext = self.editor.textCursor().selectedText()
        toFind = rtext
        self.bookmarks.setCurrentIndex(0)
        if self.bookmarks.findText(toFind, Qt.MatchContains):
            row = self.bookmarks.findText(toFind, Qt.MatchContains)
            self.statusBar().showMessage("found '" + toFind + "' at bookmark "  + str(row))
            self.bookmarks.setCurrentIndex(row)
            self.gotoBookmark()
        else:
            self.statusBar().showMessage("def not found")
            
    def clearBookmarks(self):
        self.bookmarks.clear()
    #### find lines with def or class
    def findBookmarks(self):
        self.editor.setFocus()
        self.editor.moveCursor(QTextCursor.Start)
        if not self.editor.toPlainText() == "":
            self.clearBookmarks()
            newline = "\n" #u"\2029"
            fr = "from"
            im = "import"
            d = "def"
            d2 = "    def"
            c = "class"
            sn = str("if __name__ ==")
            line = ""
            list = []
            ot = self.editor.toPlainText()
            theList  = ot.split(newline)
            linecount = ot.count(newline)
            for i in range(linecount + 1):
                if theList[i].startswith(im):
                    line = str(theList[i]).replace("'\t','[", "").replace("]", "")
                    self.bookmarks.addItem(str(line), i)
                elif theList[i].startswith(fr):
                    line = str(theList[i]).replace("'\t','[", "").replace("]", "")
                    self.bookmarks.addItem(str(line), i)
                elif theList[i].startswith(c):
                    line = str(theList[i]).replace("'\t','[", "").replace("]", "")
                    self.bookmarks.addItem(str(line), i)
                elif theList[i].startswith(tab + d):
                    line = str(theList[i]).replace(tab, "").replace("'\t','[", "").replace("]", "")
                    self.bookmarks.addItem(str(line), i)
                elif theList[i].startswith(d):
                    line = str(theList[i]).replace(tab, "").replace("'\t','[", "").replace("]", "")
                    self.bookmarks.addItem(str(line), i)
                elif theList[i].startswith(d2):
                    line = str(theList[i]).replace(tab, "").replace("'\t','[", "").replace("]", "")
                    self.bookmarks.addItem(str(line), i)
                elif theList[i].startswith(sn):
                    line = str(theList[i]).replace("'\t','[", "").replace("]", "")
                    self.bookmarks.addItem(str(line), i)
                
        self.statusBar().showMessage("bookmarks changed")
                
    def clearLabel(self):
        self.mylabel.setText("")
              
            
    def openRecentFile(self):
        action = self.sender()
        if action:
            myfile = action.data()
            print(myfile)
            if (self.maybeSave()):
                if QFile.exists(myfile):
                    self.openFileOnStart(myfile)
                else:
                    self.msgbox("Info", "File does not exist!")
            
        ### New File
    def newFile(self):
        if self.maybeSave():
            self.editor.clear()
            self.editor.setPlainText(self.mainText)
            self.filename = ""
            self.setModified(False)
            self.editor.moveCursor(self.cursor.End)
            self.statusBar().showMessage("new File created.")
            self.editor.setFocus()
            self.bookmarks.clear()
            self.setWindowTitle("new File[*]")
            
       ### open File
    def openFileOnStart(self, path=None):
        if path:
            inFile = QFile(path)
            if inFile.open(QFile.ReadWrite | QFile.Text):
                text = inFile.readAll()
                try:
                        # Python v3.
                    text = str(text, encoding = 'utf8')
                except TypeError:
                        # Python v2.
                    text = str(text)
                self.editor.setPlainText(text.replace(tab, "    "))
                self.setModified(False)
                self.setCurrentFile(path)
                self.editor.setFocus()
                self.findBookmarks()
                ### save backup
                file = QFile(self.filename + "_backup")
                if not file.open( QFile.WriteOnly | QFile.Text):
                    QMessageBox.warning(self, "Error",
                        "Cannot write file %s:\n%s." % (self.filename, file.errorString()))
                    return
                outstr = QTextStream(file)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                outstr << self.editor.toPlainText()
                QApplication.restoreOverrideCursor()  
                self.statusBar().showMessage("File '" + path + "' loaded succesfully & bookmarks added & backup created ('" + self.filename + "_backup" + "')")

             ### add all words to completer ###
#                mystr = self.editor.toPlainText()
#                self.wordList =mystr.split()
#                print(mystr)
#                self.completer.setModel(self.modelFromFile(self.root + '/resources/wordlist.txt'))
        
        ### open File
    def openFile(self, path=None):
        if self.maybeSave():
            if not path:
                path, _ = QFileDialog.getOpenFileName(self, "Open File", self.dirpath,
                    "Python Files (*.py);; all Files (*)")

            if path:
                self.openFileOnStart(path)
            
    def fileSave(self):
        if (self.filename != ""):
            file = QFile(self.filename)
            if not file.open( QFile.WriteOnly | QFile.Text):
                QMessageBox.warning(self, "Error",
                        "Cannot write file %s:\n%s." % (self.filename, file.errorString()))
                return

            outstr = QTextStream(file)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            outstr << self.editor.toPlainText()
            QApplication.restoreOverrideCursor()                
            self.setModified(False)
            self.fname = QFileInfo(self.filename).fileName() 
            self.setWindowTitle(self.fname + "[*]")
            self.statusBar().showMessage("File saved.")
            self.setCurrentFile(self.filename)
            self.editor.setFocus()
            
            
        else:
            self.fileSaveAs()
            
            ### save File
    def fileSaveAs(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save as...", self.filename,
                "Python files (*.py)")

        if not fn:
            print("Error saving")
            return False

        lfn = fn.lower()
        if not lfn.endswith('.py'):
            fn += '.py'

        self.filename = fn
        self.fname = QFileInfo(QFile(fn).fileName())
        return self.fileSave()
        
    def closeEvent(self, e):
        self.writeSettings()
        if self.maybeSave():
            e.accept()
        else:
            e.ignore()
        
        ### ask to save
    def maybeSave(self):
        if not self.isModified():
            return True

        if self.filename.startswith(':/'):
            return True

        ret = QMessageBox.question(self, "Message",
                "<h4><p>The document was modified.</p>\n" \
                "<p>Do you want to save changes?</p></h4>",
                QMessageBox.Yes | QMessageBox.Discard | QMessageBox.Cancel)

        if ret == QMessageBox.Yes:
            if self.filename == "":
                self.fileSaveAs()
                return False
            else:
                self.fileSave()
                return True

        if ret == QMessageBox.Cancel:
            return False

        return True   
        
    def about(self):
        title = "about PyEdit"
        message = """
                    <span style='color: #3465a4; font-size: 20pt;font-weight: bold;'
                    >PyEdit 2.1</strong></span></p><h3>Python Editor</h3>created by  
                    <a title='Axel Schneider' href='http://goodoldsongs.jimdo.com' target='_blank'>Axel Schneider</a> with PyQt5<br><br>
                    <span style='color: #555753; font-size: 9pt;'>©2017 Axel Schneider</strong></span></p>
                        """
        self.infobox(title, message)
        
    def runPy3(self):
        if self.editor.toPlainText() == "":
            self.statusBar().showMessage("no Code!")
            return
        if not self.editor.toPlainText() == self.mainText:
            if self.filename:
                self.mypython = "3"
                self.statusBar().showMessage("running " + self.filename + " in Python 3")
                self.fileSave()
                cmd = "python3"
                self.readData(cmd)
            else:
                self.filename = "/tmp/tmp.py"
                self.fileSave()
                self.runPy3()
        else:
            self.statusBar().showMessage("no code to run")
        
    def runPy2(self):
        if self.editor.toPlainText() == "":
            self.statusBar().showMessage("no Code!")
            return
        if not self.editor.toPlainText() == self.mainText:
            if self.filename:
                self.mypython = "2"
                self.statusBar().showMessage("running " + self.filename + " in Python 2")
                self.fileSave()
                cmd = "python"
                self.readData(cmd)
            else:
                self.filename = "/tmp/tmp.py"
                self.fileSave()
                self.runPy2()
        else:
            self.statusBar().showMessage("no code to run")
            
    def readData(self, cmd):
        self.mylabel.clear()
        dname = QFileInfo(self.filename).filePath().replace(QFileInfo(self.filename).fileName(), "")
        self.statusBar().showMessage(str(dname))
        QProcess().execute("cd '" + dname + "'")
        self.process.start(cmd,['-u', dname + self.strippedName(self.filename)])
        
    def killPython(self):
        if (self.mypython == "3"):
            cmd = "killall python3"
        else:
            cmd = "killall python"
        self.readData(cmd)
        
    def commentBlock(self):
        self.editor.copy()
        clipboard = QApplication.clipboard();
        originalText = clipboard.text()
        mt1 = tab + tab + "'''" + "\n"
        mt2 = "\n" + tab + tab + "'''"
        mt = mt1 + originalText + mt2
        clipboard.setText(mt)
        self.editor.paste()
        
    def uncommentBlock(self):
        self.editor.copy()
        clipboard = QApplication.clipboard();
        originalText = clipboard.text()
        mt1 = tab + tab + "'''" + "\n"
        mt2 = "\n" + tab + tab + "'''"
        clipboard.setText(originalText.replace(mt1, "").replace(mt2, ""))
        self.editor.paste()
        
        self.statusBar().showMessage("added block comment")
            
    def commentLine(self):
        newline = u"\u2029"
        comment = "#"
        list = []
        ot = self.editor.textCursor().selectedText()
        if not self.editor.textCursor().selectedText() == "":
            ### multiple lines selected        
            theList  = ot.splitlines()
            linecount = ot.count(newline)
            for i in range(linecount + 1):
                list.insert(i, comment + theList[i])
            self.editor.textCursor().insertText(newline.join(list))
            self.setModified(True)    
            self.statusBar().showMessage("added comment")
        else:
            ### one line selected
            self.editor.moveCursor(QTextCursor.StartOfLine)
            self.editor.textCursor().insertText("#")
            
            
    def uncommentLine(self):
        comment = "#"
        newline = u"\u2029"
        list = []
        ot = self.editor.textCursor().selectedText()
        if not self.editor.textCursor().selectedText() == "":
        ### multiple lines selected 
            theList  = ot.splitlines()
            linecount = ot.count(newline)
            for i in range(linecount + 1):
                list.insert(i, (theList[i]).replace(comment, "", 1))
            self.editor.textCursor().insertText(newline.join(list))
            self.setModified(True)    
            self.statusBar().showMessage("comment removed")
        else:
            ### one line selected
            self.editor.moveCursor(QTextCursor.StartOfLine)
            self.editor.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)
            if self.editor.textCursor().selectedText() == comment:
                self.editor.textCursor().deleteChar()
                self.editor.moveCursor(QTextCursor.StartOfLine)
            else:
                self.editor.moveCursor(QTextCursor.StartOfLine)
        
    def goToLine(self, ft):
        self.editor.moveCursor(int(self.gofield.currentText()),
                                QTextCursor.MoveAnchor) ### not working
        
    def findText(self):
        word = self.findfield.text()
        if self.editor.find(word):
            linenumber = self.editor.textCursor().blockNumber() + 1
            self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
            self.editor.centerCursor()
        else:
            self.statusBar().showMessage("<b>'" + self.findfield.text() + "'</b> not found")
            self.editor.moveCursor(QTextCursor.Start)            
            if self.editor.find(word):
                linenumber = self.editor.textCursor().blockNumber() + 1
                self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
                self.editor.centerCursor()
            
    def findBookmark(self, word):
        if self.editor.find(word):
            linenumber = self.getLineNumber() #self.editor.textCursor().blockNumber() + 1
            self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
            
    def handleQuit(self):
        if self.maybeSave():
            print("Goodbye ...")
            app.quit()

    def set_numbers_visible(self, value = True):
        self.numbers.setVisible(False)

    def match_left(self, block, character, start, found):
        map = {'{': '}', '(': ')', '[': ']'}

        while block.isValid():
            data = block.userData()
            if data is not None:
                braces = data.braces
                N = len(braces)

                for k in range(start, N):
                    if braces[k].character == character:
                        found += 1

                    if braces[k].character == map[character]:
                        if not found:
                            return braces[k].position + block.position()
                        else:
                            found -= 1

                block = block.next()
                start = 0

    def match_right(self, block, character, start, found):
        map = {'}': '{', ')': '(', ']': '['}

        while block.isValid():
            data = block.userData()

            if data is not None:
                braces = data.braces

                if start is None:
                    start = len(braces)
                for k in range(start - 1, -1, -1):
                    if braces[k].character == character:
                        found += 1
                    if braces[k].character == map[character]:
                        if found == 0:
                            return braces[k].position + block.position()
                        else:
                            found -= 1
            block = block.previous()
            start = None


        cursor = self.editor.textCursor()
        block = cursor.block()
        data = block.userData()
        previous, next = None, None

        if data is not None:
            position = cursor.position()
            block_position = cursor.block().position()
            braces = data.braces
            N = len(braces)

            for k in range(0, N):
                if braces[k].position == position - block_position or braces[k].position == position - block_position - 1:
                    previous = braces[k].position + block_position
                    if braces[k].character in ['{', '(', '[']:
                        next = self.match_left(block,
                                               braces[k].character,
                                               k + 1, 0)
                    elif braces[k].character in ['}', ')', ']']:
                        next = self.match_right(block,
                                                braces[k].character,
                                                k, 0)
                    if next is None:
                        next = -1

        if next is not None and next > 0:
            if next == 0 and next >= 0:
                format = QTextCharFormat()

            cursor.setPosition(previous)
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)

            format.setBackground(QColor('white'))
            self.left_selected_bracket.format = format
            self.left_selected_bracket.cursor = cursor

            cursor.setPosition(next)
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)

            format.setBackground(QColor('white'))
            self.right_selected_bracket.format = format
            self.right_selected_bracket.cursor = cursor

    def paintEvent(self, event):
        highlighted_line = QTextEdit.ExtraSelection()
        highlighted_line.format.setBackground(lineHighlightColor)
        highlighted_line.format.setProperty(QTextFormat
                                                 .FullWidthSelection,
                                                  QVariant(True))
        highlighted_line.cursor = self.editor.textCursor()
        highlighted_line.cursor.clearSelection()
        self.editor.setExtraSelections([highlighted_line,
                                      self.left_selected_bracket,
                                      self.right_selected_bracket])

    def document(self):
        return self.editor.document
        
    def isModified(self):
        return self.editor.document().isModified()

    def setModified(self, modified):
        self.editor.document().setModified(modified)

    def setLineWrapMode(self, mode):
        self.editor.setLineWrapMode(mode)

    def clear(self):
        self.editor.clear()

    def setPlainText(self, *args, **kwargs):
        self.editor.setPlainText(*args, **kwargs)

    def setDocumentTitle(self, *args, **kwargs):
        self.editor.setDocumentTitle(*args, **kwargs)

    def set_number_bar_visible(self, value):
        self.numbers.setVisible(value)
        
    def replaceAll(self):
        if not self.editor.document().toPlainText() == "":
            if not self.findfield.text() == "":
                self.statusBar().showMessage("replacing all")
                oldtext = self.editor.document().toPlainText()
                newtext = oldtext.replace(self.findfield.text(), self.replacefield.text())
                self.editor.setPlainText(newtext)
                self.setModified(True)
            else:
                self.statusBar().showMessage("nothing to replace")
        else:
                self.statusBar().showMessage("no text")
        
    def replaceOne(self):
        if not self.editor.document().toPlainText() == "":
            if not self.findfield.text() == "":
                self.statusBar().showMessage("replacing all")
                oldtext = self.editor.document().toPlainText()
                newtext = oldtext.replace(self.findfield.text(), self.replacefield.text(), 1)
                self.editor.setPlainText(newtext)
                self.setModified(True)
            else:
                self.statusBar().showMessage("nothing to replace")
        else:
                self.statusBar().showMessage("no text")
        
    def setCurrentFile(self, fileName):
        self.filename = fileName
        if self.filename:
            self.setWindowTitle(self.strippedName(self.filename) + "[*]")
        else:
            self.setWindowTitle("no File")      
        
        files = self.settings.value('recentFileList', [])

        try:
            files.remove(fileName)
        except ValueError:
            pass

        if not fileName == "/tmp/tmp.py":
            files.insert(0, fileName)
        del files[self.MaxRecentFiles:]

        self.settings.setValue('recentFileList', files)

        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, myEditor):
                widget.updateRecentFileActions()

    def updateRecentFileActions(self):
        mytext = ""
        files = self.settings.value('recentFileList', [])

        numRecentFiles = min(len(files), self.MaxRecentFiles)

        for i in range(numRecentFiles):
            text = "&%d %s" % (i + 1, self.strippedName(files[i]))
            self.recentFileActs[i].setText(text)
            self.recentFileActs[i].setData(files[i])
            self.recentFileActs[i].setVisible(True)
            self.recentFileActs[i].setIcon(QIcon.fromTheme("gnome-mime-text-x-python"))

        for j in range(numRecentFiles, self.MaxRecentFiles):
            self.recentFileActs[j].setVisible(False)

        self.separatorAct.setVisible((numRecentFiles > 0))
        
    def strippedName(self, fullFileName):
        return QFileInfo(fullFileName).fileName()
        
    def clearRecentFiles(self):
        self.settings.setValue('recentFileList', [])
        self.updateRecentFileActions()

    def readSettings(self):
        if self.settings.value("pos") != "":
            pos = self.settings.value("pos", QPoint(200, 200))
            self.move(pos)
        if self.settings.value("size") != "":
            size = self.settings.value("size", QSize(400, 400))
            self.resize(size)

    def writeSettings(self):
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("size", self.size())
        
    def msgbox(self,title, message):
        QMessageBox.warning(self, title, message)
        
    def infobox(self,title, message):
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self, Qt.Dialog|Qt.NoDropShadowWindowHint).show()        
        
    def insertTemplate(self):
        line = int(self.getLineNumber())
        path = self.appfolder + "/templates/" + self.templates.itemText(self.templates.currentIndex()) + ".txt"
        if path:
            inFile = QFile(path)
            if inFile.open(QFile.ReadOnly | QFile.Text):
                text = inFile.readAll()
                self.editor.setFocus()
                try: ### python 3
                    self.editor.textCursor().insertText(str(text, encoding = 'utf8'))
                except TypeError:  ### python 2
                    self.editor.textCursor().insertText(str(text))
                self.setModified(True)
                self.findBookmarks()
                self.statusBar().showMessage("'" + self.templates.itemText(self.templates.currentIndex()) + "' inserted")
                inFile.close()
                text = ""
                self.selectLine(line)
            else:
                self.statusBar().showMessage("error loadind Template")
            
    def selectLine(self, line):
        linecursor = QTextCursor(self.editor.document().findBlockByLineNumber(line-1))
        self.editor.moveCursor(QTextCursor.End)
        self.editor.setTextCursor(linecursor)
        
    def createTrayIcon(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Systray",
                    "I couldn't detect any system tray on this system.")
        else:
            self.trayIcon = QSystemTrayIcon(self)
            self.trayIcon.setIcon(QIcon.fromTheme("applications-python"))
            self.trayIconMenu = QMenu(self)
            self.trayIconMenu.addAction(QAction(QIcon.fromTheme("applications-python"), "about PyEdit", self, triggered=self.about))
            self.trayIconMenu.addSeparator()
            self.trayIconMenu.addAction(QAction(QIcon.fromTheme("application-exit"),"Exit", self, triggered=self.handleQuit))
            self.trayIcon.setContextMenu(self.trayIconMenu)
        
    def handlePrint(self):
        if self.editor.toPlainText() == "":
            self.statusBar().showMessage("no text")
        else:
            dialog = QtPrintSupport.QPrintDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.handlePaintRequest(dialog.printer())
                self.statusBar().showMessage("Document printed")
            
    def handlePrintPreview(self):
        if self.editor.toPlainText() == "":
            self.statusBar().showMessage("no text")
        else:
            dialog = QtPrintSupport.QPrintPreviewDialog()
            dialog.setFixedSize(900,650)
            dialog.paintRequested.connect(self.handlePaintRequest)
            dialog.exec_()
            self.statusBar().showMessage("Print Preview closed")

    def handlePaintRequest(self, printer):
        printer.setDocName(self.filename)
        document = self.editor.document()
        document.print_(printer)

    def modelFromFile(self, fileName):
        f = QFile(fileName)
        if not f.open(QFile.ReadOnly):
            return QStringListModel(self.completer)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        self.words = []
        while not f.atEnd():
            line = f.readLine().trimmed()
            if line.length() != 0:
                try:
                    line = str(line, encoding='ascii')
                except TypeError:
                    line = str(line)

                self.words.append(line)
#                print("\n".join(self.wordList))
#                self.words.append("\n".join(self.wordList))

        QApplication.restoreOverrideCursor()

        return QStringListModel(self.words, self.completer)
                
  
def stylesheet2(self):
    return """
QPlainTextEdit
{
font-family: Helvetica;
font-size: 13px;
background: #E2E2E2;
color: #202020;
border: 1px solid #1EAE3D;
}
QTextEdit
{
background: #292929;
color: #1EAE3D;
font-family: Monospace;
font-size: 8pt;
padding-left: 6px;
border: 1px solid #1EAE3D;
}
QStatusBar
{
font-family: Helvetica;
color: #204a87;
font-size: 8pt;
}
QLabel
{
font-family: Helvetica;
color: #204a87;
font-size: 8pt;
}
QLineEdit
{
font-family: Helvetica;
font-size: 8pt;
}
QPushButton
{
font-family: Helvetica;
font-size: 8pt;
}
QComboBox
{
font-family: Helvetica;
font-size: 8pt;
}
QMenuBar
{
font-family: Helvetica;
font-size: 8pt;
}
QMenu
{
font-family: Helvetica;
font-size: 8pt;
}
QToolBar
{
background: transparent;
}
    """       

if __name__ == '__main__':
    app = QApplication(argv)
    translator = QTranslator(app)
    locale = QLocale.system().name()
    print(locale)
    path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    print(path)
    translator.load('qt_%s' % locale, path)
    app.installTranslator(translator)
    win = myEditor()
    win.setWindowTitle("PyEdit" + "[*]")
    win.show()
    if len(argv) > 1:
        print(argv[1])
        win.openFileOnStart(argv[1])

    sys.exit(app.exec_())
