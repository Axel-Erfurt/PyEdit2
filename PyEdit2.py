#!/usr/bin/python3
# -- coding: utf-8 --

from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QApplication, QFileDialog, QMessageBox, QHBoxLayout, \
                         QFrame, QTextEdit, QToolBar, QComboBox, QLabel, QAction, QLineEdit, QToolButton, QMenu, QMainWindow
from PyQt5.QtGui import QIcon, QPainter, QTextFormat, QColor, QTextCursor, QKeySequence, QClipboard
from PyQt5.QtCore import Qt, QVariant, QRect, QDir, QFile, QFileInfo, QTextStream, QRegExp, QSettings
from PyQt5 import QtTest
import sys, os
import subprocess
import syntax_py
from pathlib import Path

lineBarColor = QColor("#DED6AC")
lineHighlightColor  = QColor("#F5F5F5")

class NumberBar(QWidget):
    def __init__(self, parent = None):
        super(NumberBar, self).__init__(parent)
        self.editor = parent
        layout = QVBoxLayout()
        self.setLayout(layout)
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
        width = self.fontMetrics().width(str(string)) + 10
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

                rect = QRect(0, block_top, self.width() - 5, height)

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
        self.MaxRecentFiles = 5
        self.windowList = []
        self.recentFileActs = []
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Editor Widget ...
        QIcon.setThemeName('Faenza-Dark')
        self.editor = QPlainTextEdit() 
        self.editor.setStyleSheet(stylesheet2(self))
        self.editor.setFrameStyle(QFrame.NoFrame)
        self.editor.setTabStopWidth(14)
        self.extra_selections = []
        self.mainText = "#!/usr/bin/python3\n# -*- coding: utf-8 -*-\n"
        self.fname = ""
        self.filename = ""
        self.mypython = "2"
        self.sh = subprocess
        self.mylabel = QLabel()
        self.mylabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # Line Numbers ...
        self.numbers = NumberBar(self.editor)
        self.createActions()
        # Syntax Highlighter ...
        self.highlighter = syntax_py.Highlighter(self.editor.document())

        # Laying out...
        layoutH = QHBoxLayout()
        layoutH.setSpacing(1.5)
        layoutH.addWidget(self.numbers)
        layoutH.addWidget(self.editor)
        
        ### begin toolbar
        tb = QToolBar(self)
        tb.setWindowTitle("File Toolbar")        
        ### file buttons
        self.newAct = QAction("&New", self, shortcut=QKeySequence.New,
#!/usr/bin/python3
# -- coding: utf-8 --

from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QApplication, QFileDialog, QMessageBox, QHBoxLayout, \
                             QFrame, QTextEdit, QToolBar, QComboBox, QLabel, QAction, QLineEdit, QToolButton, QMenu, QMainWindow, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QTextFormat, QColor, QTextCursor, QKeySequence, QClipboard
from PyQt5.QtCore import Qt, QVariant, QRect, QDir, QFile, QFileInfo, QTextStream, QRegExp, QSettings, QProcess
from PyQt5 import QtTest
import sys, os
import subprocess
import syntax_py
from pathlib import Path

lineBarColor = QColor("#DED6AC")
lineHighlightColor  = QColor("#F5F5F5")

class NumberBar(QWidget):
    def __init__(self, parent = None):
        super(NumberBar, self).__init__(parent)
        self.editor = parent
        layout = QVBoxLayout()
        self.setLayout(layout)
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
        width = self.fontMetrics().width(str(string)) + 10
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

                rect = QRect(0, block_top, self.width() - 5, height)

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
        self.MaxRecentFiles = 10
        self.windowList = []
        self.recentFileActs = []
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Editor Widget ...
        QIcon.setThemeName('Faenza-Dark')
        self.editor = QPlainTextEdit() 
        self.editor.setStyleSheet(stylesheet2(self))
        self.editor.setFrameStyle(QFrame.NoFrame)
        self.editor.setTabStopWidth(14)
        self.extra_selections = []
        self.mainText = "#!/usr/bin/python3\n# -*- coding: utf-8 -*-\n"
        self.fname = ""
        self.filename = ""
        self.mypython = "2"
        self.sh = subprocess
        self.mylabel = QTextEdit()
        self.mylabel.setFixedHeight(70)
        self.mylabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # Line Numbers ...
        self.numbers = NumberBar(self.editor)
        self.createActions()
        # Syntax Highlighter ...
        self.highlighter = syntax_py.Highlighter(self.editor.document())

        # Laying out...
        layoutH = QHBoxLayout()
        layoutH.setSpacing(1.5)
        layoutH.addWidget(self.numbers)
        layoutH.addWidget(self.editor)
        
        ### begin toolbar
        tb = QToolBar(self)
        tb.setWindowTitle("File Toolbar")        
        ### file buttons
        self.newAct = QAction("&New", self, shortcut=QKeySequence.New,
                statusTip="Create a new file", triggered=self.newFile)
        self.newAct.setIcon(QIcon.fromTheme("document-new"))
        tb.addAction(self.newAct)
        
        self.openAct = QAction("&Open", self, shortcut=QKeySequence.Open,
                statusTip="open file", triggered=self.openFile)
        self.openAct.setIcon(QIcon.fromTheme("document-open"))
        tb.addAction(self.openAct)

        self.saveAct = QAction("&Save", self, shortcut=QKeySequence.Save,
                statusTip="save file", triggered=self.fileSave)
        self.saveAct.setIcon(QIcon.fromTheme("document-save"))
        tb.addAction(self.saveAct)
        
        self.saveAsAct = QAction("&Save as ...", self, shortcut=QKeySequence.SaveAs,
                statusTip="save file as ...", triggered=self.fileSaveAs)
        self.saveAsAct.setIcon(QIcon.fromTheme("document-save-as"))
        tb.addAction(self.saveAsAct)
        
        ### comment buttons       
        tb.addSeparator()           
        self.commentAct = QAction("#comment Line", self, shortcut="F2",
                toolTip="comment Line (F2)", triggered=self.commentLine)
        tb.addAction(self.commentAct)
                         
        self.uncommentAct = QAction("uncomment Line", self, shortcut="F3",
                toolTip="uncomment Line (F3)", triggered=self.uncommentLine)
        tb.addAction(self.uncommentAct)  
        
        self.commentBlockAct = QAction("/* - */", self, shortcut="F6",
                toolTip="comment selected block (F6)", triggered=self.commentBlock)
        tb.addAction(self.commentBlockAct)  
        
        self.uncommentBlockAct = QAction("&uncomment Block (F7)", self, shortcut="F7",
                toolTip="uncomment selected block (F7)", triggered=self.uncommentBlock)
        self.uncommentBlockAct.setIcon(QIcon.fromTheme("emblem-noread"))
        tb.addAction(self.uncommentBlockAct)     
        ### run python buttons      
        tb.addSeparator()   
        self.py2Act = QAction("run in Python 2 (F4)", self, shortcut="F4",
                toolTip="run in Python 2", triggered=self.runPy2)
        self.py2Act.setIcon(QIcon.fromTheme("gnome-mime-text-x-python"))
        tb.addAction(self.py2Act)                               
        self.py3Act = QAction("run in Python 3 (F5)", self, shortcut="F5",
                toolTip="run in Python 3", triggered=self.runPy3)
        self.py3Act.setIcon(QIcon.fromTheme("gnome-mime-text-x-python"))
        tb.addAction(self.py3Act)
               
        ### about buttons
        tb.addSeparator()
        tb.addAction(QIcon.fromTheme("dialog-question"),"&About PyEdit", self.about)
        tb.addSeparator()
        tb.addAction(QIcon.fromTheme("dialog-info"),"About &PyQT", QApplication.instance().aboutQt)
        tb.addSeparator()
        tb.addAction(QIcon.fromTheme("gtk-refresh"),"clear Output Label", self.clearLabel)
        ### exit button
        self.exitAct = QAction("exit", self, shortcut=QKeySequence.Quit,
                toolTip="Exit", triggered=self.handleQuit)
        self.exitAct.setIcon(QIcon.fromTheme("application-exit"))
        tb.addAction(self.exitAct)     
        ### end toolbar
        
        ### find / replace toolbar
        self.tbf = QToolBar(self)
        self.tbf.setWindowTitle("Find Toolbar")   
        self.findfield = QLineEdit()
        self.findfield.addAction(QIcon.fromTheme("edit-find"), QLineEdit.LeadingPosition)
        self.findfield.setClearButtonEnabled(True)
        self.findfield.setFixedWidth(150)
        self.findfield.setPlaceholderText("find")
        self.findfield.setToolTip("press RETURN to find")
        self.findfield.setText("")
        ft = self.findfield.text()
        self.findfield.returnPressed.connect(self.findText)
        self.tbf.addWidget(self.findfield)
        self.replacefield = QLineEdit()
        self.replacefield.addAction(QIcon.fromTheme("edit-find-and-replace"), QLineEdit.LeadingPosition)
        self.replacefield.setClearButtonEnabled(True)
        self.replacefield.setFixedWidth(150)
        self.replacefield.setPlaceholderText("replace with")
        self.replacefield.setToolTip("press RETURN to replace the first")
        self.replacefield.returnPressed.connect(self.replaceOne)
        self.tbf.addSeparator() 
        self.tbf.addWidget(self.replacefield)
        self.tbf.addSeparator()
        
        self.tbf.addAction("replace all", self.replaceAll)
        self.tbf.addSeparator()
        
        self.gotofield = QLineEdit()
        self.gotofield.addAction(QIcon.fromTheme("next"), QLineEdit.LeadingPosition)
        self.gotofield.setClearButtonEnabled(True)
        self.gotofield.setFixedWidth(120)
        self.gotofield.setPlaceholderText("go to line")
        self.gotofield.setToolTip("press RETURN to go to line")
        self.gotofield.returnPressed.connect(self.gotoLine)
        self.tbf.addWidget(self.gotofield)
        
        self.tbf.addSeparator() 
        self.bookmarks = QComboBox()
        self.bookmarks.setFixedWidth(200)
        self.bookmarks.setToolTip("go to bookmark")
        self.bookmarks.activated.connect(self.gotoBookmark)
        self.tbf.addWidget(self.bookmarks)

        self.bookAct = QAction("add Bookmark", self,
                toolTip="add Bookmark", triggered=self.addBookmark)
        self.bookAct.setIcon(QIcon.fromTheme("previous"))
        self.tbf.addAction(self.bookAct)
        
        self.tbf.addSeparator()
        self.bookrefresh = QAction("update Bookmarks", self,
                toolTip="update Bookmarks", triggered=self.findBookmarks)
        self.bookrefresh.setIcon(QIcon.fromTheme("view-refresh"))
        self.tbf.addAction(self.bookrefresh)

        layoutV = QVBoxLayout()
        
        bar=self.menuBar()
        self.filemenu=bar.addMenu("File")
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
        self.filemenu.addAction(self.exitAct)
        
        editmenu = bar.addMenu("Edit")
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
        editmenu.addAction(self.py2Act)
        editmenu.addAction(self.py3Act)
        layoutV.addWidget(bar)      
        
        layoutV.addWidget(tb)
        layoutV.addWidget(self.tbf)
        layoutV.addLayout(layoutH)
        self.mylabel.setMinimumHeight(28)
        self.mylabel.setStyleSheet(stylesheet2(self))
        self.mylabel.setText("Welcome to PyEdit2")
        layoutV.addWidget(self.mylabel)
        ### main window
        mq = QWidget(self)
        mq.setLayout(layoutV)
        self.setCentralWidget(mq)
        
        # Event Filter ...
        self.installEventFilter(self)
        self.editor.setFocus()
        self.cursor = QTextCursor()
        self.editor.setPlainText(self.mainText)
        self.editor.moveCursor(self.cursor.End)
        self.editor.document().modificationChanged.connect(self.setWindowModified)
        
        # Brackets ExtraSelection ...
        self.left_selected_bracket  = QTextEdit.ExtraSelection()
        self.right_selected_bracket = QTextEdit.ExtraSelection()
        
        self.process = QProcess(self)
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(lambda: self.mylabel.append("starting shell"))
        self.process.finished.connect(lambda: self.mylabel.append("shell ended"))
        
    def dataReady(self):
        out = ""
        try:
            out = str(self.process.readAll(), encoding = 'utf8').rstrip() #readAllStandardOutput())
        except TypeError:
            out = str(self.process.readAll()).rstrip()
        self.mylabel.append(out)
        self.mylabel.moveCursor(self.cursor.End)
        self.mylabel.ensureCursorVisible()
        
    def createActions(self):
        for i in range(self.MaxRecentFiles):
            self.recentFileActs.append(
                   QAction(self, visible=False,
                            triggered=self.openRecentFile))
            
    def addBookmark(self):
        self.editor.moveCursor(self.cursor.StartOfLine)
        linenumber = self.editor.textCursor().blockNumber() + 1
        linetext = self.editor.textCursor().block().text()
        self.bookmarks.addItem(linetext, linenumber)
            
    def gotoLine(self, ln):
        ln = int(self.gotofield.text())
        linecursor = QTextCursor(self.editor.document().findBlockByLineNumber(ln-1))
        self.editor.moveCursor(QTextCursor.End)
        self.editor.setTextCursor(linecursor)
        
    def gotoBookmark(self):
        self.editor.moveCursor(QTextCursor.Start)
        linetext = self.bookmarks.itemText(self.bookmarks.currentIndex())
        self.findBookmark(linetext)
        linenumber = self.editor.textCursor().blockNumber() + 1
        ln = int(linenumber)
        linecursor = QTextCursor(self.editor.document().findBlockByLineNumber(ln))
        self.editor.moveCursor(QTextCursor.End)
        self.editor.setTextCursor(linecursor)
        
    def clearBookmarks(self):
        self.bookmarks.clear()
            
    #### find lines with def or class
    def findBookmarks(self):
        self.clearBookmarks()
        self.editor.moveCursor(QTextCursor.Start)
        QtTest.QTest.qWait(250)
        while True:
            r = self.editor.find("class")
            if r:
                self.addBookmark()
                self.cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)
                self.editor.find("class")            
            else:
                break
        while True:
            r = self.editor.find("def")
            if r:
                self.addBookmark()
                self.cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)
                self.editor.find("def")
            else:
                break
        self.editor.moveCursor(QTextCursor.Start)

                
    def clearLabel(self):
        self.mylabel.setText("")
              
            
    def openRecentFile(self):
        action = self.sender()
        if action:
            if (self.maybeSave()):
                self.openFileOnStart(action.data())
            
        ### New File
    def newFile(self):
        if self.maybeSave():
            self.editor.clear()
            self.editor.setPlainText(self.mainText)
            self.filename = ""
            self.setModified(False)
            self.editor.moveCursor(self.cursor.End)
            self.mylabel.setText("new File created.")
            self.editor.setFocus()
            
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
                self.editor.setPlainText(text)
                self.filename = path
                self.setModified(False)
                self.fname = QFileInfo(path).fileName() 
                self.setWindowTitle(self.fname + "[*]")
                self.document = self.editor.document()
                self.mylabel.setText("File '" + self.fname + "' loaded succesfully.")
                self.setCurrentFile(self.filename)
                self.editor.setFocus()
                self.findBookmarks()
        
        ### open File
    def openFile(self, path=None):
        if self.maybeSave():
            if not path:
                path, _ = QFileDialog.getOpenFileName(self, "Open File", QDir.homePath() + "/Documents/python_files/",
                    "Python Files (*.py)")

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
            self.mylabel.setText("File saved.")
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
        self.fname = os.path.splitext(str(fn))[0].split("/")[-1]
        return self.fileSave()
        
    def closeEvent(self, e):
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
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

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
        title = "About PyEdit"
        message = "<p><h2>PyEdit</h1></p>" \
                "\n<p>created by Axel Schneider</p>"  \
                "\n<p>with PyQt5</p>"  \
                "\n<p><h3>©2016</h1></p>" \
                "\n<p><a>https://goodoldsongs.jimdo.com</a></p>\n"
        msg = QMessageBox.information(self, title, message, QMessageBox.Close)
        
    def runPy3(self):
        if self.filename:
            self.mypython = "3"
            self.mylabel.setText("running " + self.filename + " in Python 3")
            self.fileSave()
            dname = os.path.abspath(os.path.join(self.filename, os.pardir))
            os.chdir(dname)
            cmd = "python3"
            self.readData(cmd)
        
    def runPy2(self):
        if self.filename:
            self.mypython = "2"
            self.mylabel.setText("running " + self.filename + " in Python 2")
            self.fileSave()
            dname = os.path.abspath(os.path.join(self.filename, os.pardir))
            os.chdir(dname)
            cmd = "python"
            self.readData(cmd)
            
    def readData(self, cmd):
        self.process.start(cmd,['-u', self.filename])
        
    def killPython(self):
        if (self.mypython == "3"):
            cmd = "killall python3"
        elif (self.mypython == "2"):
            cmd = "killall python"
        self.readData(cmd)
        
    def commentBlock(self):
        self.editor.copy()
        clipboard = QApplication.clipboard();
        originalText = clipboard.text()
        clipboard.setText("/*" + originalText + "*/")
        self.editor.paste()
        
    def uncommentBlock(self):
        self.editor.copy()
        clipboard = QApplication.clipboard();
        originalText = clipboard.text()
        clipboard.setText(originalText.replace("*/", "").replace("/*", ""))
        self.editor.paste()
        
        self.mylabel.setText("added block comment")
            
    def commentLine(self):
        self.editor.moveCursor(self.cursor.StartOfLine)
        self.editor.insertPlainText("#")
        self.mylabel.setText("added line comment")
        
    def uncommentLine(self):
        self.deleteComment()
        
    def deleteComment(self):
        self.cursor.clearSelection()
        self.editor.moveCursor(self.cursor.StartOfLine, self.cursor.MoveAnchor)
        self.editor.moveCursor(self.cursor.Right, self.cursor.KeepAnchor)
        self.cursor.select(QTextCursor.BlockUnderCursor)
        self.editor.insertPlainText("")
        self.mylabel.setText("removed line comment")
        
    def goToLine(self, ft):
        self.editor.moveCursor(int(self.gofield.currentText()),
                                QTextCursor.MoveAnchor) ### not working
        
    def findText(self):
        word = self.findfield.text()
        if self.editor.find(word):
            linenumber = self.editor.textCursor().blockNumber() + 1
            self.mylabel.setText("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
        else:
            self.mylabel.setText("<b>'" + self.findfield.text() + "'</b> not found")
            self.editor.moveCursor(QTextCursor.Start)            
            if self.editor.find(word):
                linenumber = self.editor.textCursor().blockNumber() + 1
                self.mylabel.setText("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
            
    def findBookmark(self, word):
        if self.editor.find(word):
            linenumber = self.editor.textCursor().blockNumber() + 1
            self.mylabel.setText("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
            
    def handleQuit(self):
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
#    '''

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
#            '''
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
        print("replacing all")
        oldtext = self.editor.document().toPlainText()
        newtext = oldtext.replace(self.findfield.text(), self.replacefield.text())
        self.editor.setPlainText(newtext)
        self.setModified(True)
        
    def replaceOne(self):
        print("replacing all")
        oldtext = self.editor.document().toPlainText()
        newtext = oldtext.replace(self.findfield.text(), self.replacefield.text(), 1)
        self.editor.setPlainText(newtext)
        self.setModified(True)
        
    def setCurrentFile(self, fileName):
        settings = QSettings('Axel Schneider', 'PyEdit')
        files = settings.value('recentFileList')

        try:
            files.remove(fileName)
        except ValueError:
            pass

        files.insert(0, fileName)
        del files[self.MaxRecentFiles:]

        settings.setValue('recentFileList', files)

        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, myEditor):
                widget.updateRecentFileActions()

    def updateRecentFileActions(self):
        mytext = ""
        settings = QSettings('Axel Schneider', 'PyEdit')
        files = settings.value('recentFileList')

        numRecentFiles = min(len(files), self.MaxRecentFiles)

        for i in range(numRecentFiles):
            text = "&%d %s" % (i + 1, self.strippedName(files[i]))
            self.recentFileActs[i].setText(text)
            self.recentFileActs[i].setData(files[i])
            self.recentFileActs[i].setVisible(True)

        for j in range(numRecentFiles, self.MaxRecentFiles):
            self.recentFileActs[j].setVisible(False)

        self.separatorAct.setVisible((numRecentFiles > 0))
        
    def strippedName(self, fullFileName):
        return QFileInfo(fullFileName).fileName()
  
def stylesheet2(self):
    return """
QPlainTextEdit
{
background: #E2E2E2;
color: #202020;
border: 1px solid #1EAE3D;
}
QTextEdit
{
background: #292929;
color: #1EAE3D;
font-size: 8pt;
padding-left: 6px;
border: 1px solid #1EAE3D;
}    
    """       

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = myEditor()
    win.setWindowIcon(QIcon.fromTheme("gnome-mime-text-x-python"))
    win.setWindowTitle("PyEdit" + "[*]")
    win.setMinimumSize(640,250)
    win.showMaximized()
    if len(sys.argv) > 1:
        print(sys.argv[1])
        win.openFileOnStart(sys.argv[1])
    app.exec_()
      