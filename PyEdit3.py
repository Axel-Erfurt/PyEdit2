#!/usr/bin/python3
# -- coding: utf-8 --

# "© 2017 Axel Schneider <axel99092@gmail.com> https://goodoldsongs.jimdo.com/"
# "© QScintilla

from __future__ import print_function
import PyQt5
from PyQt5.QtWidgets import (QPlainTextEdit, QWidget, QVBoxLayout, QApplication, QFileDialog, QMessageBox, 
                            QLabel, QCompleter, QHBoxLayout, QTextEdit, QToolBar, QComboBox, QAction, 
                            QLineEdit, QDialog, QPushButton, QSizePolicy, QToolButton, QMenu, 
                            QMainWindow, QInputDialog, QColorDialog, QStatusBar, QSystemTrayIcon)
from PyQt5.QtGui import (QIcon, QPainter, QTextFormat, QColor, QTextCursor, QKeySequence, 
                        QClipboard, QTextDocument, QPixmap, QStandardItemModel, QStandardItem, 
                        QCursor, QFontMetrics, QFont,  QDesktopServices)
from PyQt5.QtCore import (Qt, QVariant, QRect, QDir, QFile, QFileInfo, QTextStream, QSettings, QUrl, 
                            QProcess, QPoint, QSize, QCoreApplication, QLibraryInfo)
from PyQt5 import QtPrintSupport
import os
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs, QsciPrinter, QsciScintillaBase
import keyword
import pkgutil
import Manual

tab = chr(9)
eof = "\n"
iconsize = QSize(16, 16)
#####################################################################
        
        
class QSC(QsciScintilla):
    ARROW_MARKER_NUM = 8

    def __init__(self, parent=None):
        super(QSC, self).__init__(parent)

        self.comment_str = "#"
        
        self.setEolMode(QsciScintilla.EolUnix)
        self.setUtf8(True)
        # Set the default font
        font = QFont()
        font.setFamily('Noto Mono')
        font.setFixedPitch(True)
        font.setPointSize(9)
        self.setFont(font)
        self.setMarginsFont(font)
        
        self.setSelectionBackgroundColor(QColor("#3465a4"))

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("0000") + 4)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#babdb6"))
        self.setMarginsForegroundColor(QColor("#204a87"))

        self.setFoldMarginColors(QColor("#e2e2e2"), QColor("#d2d2d2"))

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.marginClicked.connect(self.on_margin_clicked)
        self.markerDefine(QsciScintilla.RightArrow,
            self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QColor("#cc0000"),
            self.ARROW_MARKER_NUM)
        self.setMarkerForegroundColor(QColor("#eeeeec"),
            self.ARROW_MARKER_NUM)

        ### Brace matching
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        ### Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#d3d7cf"))

        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setBackspaceUnindents(True)
        self.setAutoIndent(True)
        
        ### Wrap
        self.setWrapMode(QsciScintilla.SC_WRAP_WORD)
        self.setWrapVisualFlags(QsciScintilla.WrapFlagInMargin) ### WrapFlagByText WrapFlagByBorder WrapFlagInMargin
        self.setWrapIndentMode(QsciScintilla.WrapIndentSame)
        
        self.setEdgeMode(QsciScintilla.EdgeBackground)
        self.setEdgeColumn(120)
        edge_color = caret_fg_color = QColor("#ff0000")
        self.setEdgeColor(edge_color)

        ### Set Python lexer
        lexer = QsciLexerPython(self)
        lexer.setDefaultFont(font)
        lexer.setDefaultPaper(QColor("#e2e2e2"))
        lexer.setColor(QColor('#8f5902'), QsciLexerPython.DoubleQuotedString)
        lexer.setColor(QColor('#8f5902'), QsciLexerPython.SingleQuotedString)
        lexer.setColor(QColor('#204a87'), QsciLexerPython.Keyword)
        lexer.setColor(QColor('#a40000'), QsciLexerPython.Number)
        lexer.setColor(QColor('#a40000'), QsciLexerPython.ClassName)
        lexer.setColor(QColor('#cc0000'), QsciLexerPython.FunctionMethodName)
        lexer.setColor(QColor('#a40000'), QsciLexerPython.Operator)
        lexer.setColor(QColor('#1c1c1c'), QsciLexerPython.Identifier)
        lexer.setColor(QColor('#888a85'), QsciLexerPython.CommentBlock)
        lexer.setIndentationWarning (QsciLexerPython.Inconsistent)

        lexer.setFoldComments(True)
        lexer.setFoldCompact(True)

        self.setLexer(lexer)

        ## setup autocompletion
        path = os.path.dirname(PyQt5.__file__)
        self.api = QsciAPIs(lexer)
        pyqt_path = os.path.join(path, 'Qt/qsci/api/python/PyQt5.api')
        py3_path = os.path.join(path, 'Qt/qsci/api/python/Python-3.6.api')
        if self.api.load(py3_path):
            print("python3 api loaded")
        else:
            print("python3 api not loaded!")
            
        if self.api.load(pyqt_path):
            print("Qt5 api loaded")
        else:
            print("Qt5 api not loaded!")
#
        for key in keyword.kwlist + dir(__builtins__):
            self.api.add(key)
        
        for importer, name, ispkg in pkgutil.iter_modules():
            self.api.add(name)
        
        self.api.prepare()

        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionShowSingle(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusAlways)
        self.autoCompleteFromAll()

        text = bytearray(str.encode("Noto Mono"))
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, text)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        self.SendScintilla(QsciScintilla.SCI_SETVSCROLLBAR, 1, 0)
        self.ScrollWidthTracking = True
        self.ScrollWidth = 0
        
        self.selectionChanged.connect(self.getSelectionFromEditor)

        self.setCaretWidth(2)
        self.setFolding(QsciScintilla.FoldStyle(QsciScintilla.BoxedTreeFoldStyle), margin = 2) 
        self.setCaretForegroundColor(QColor("#cc0000"))
        ### BoxedFoldStyle, CircledTreeFoldStyle, BoxedTreeFoldStyle
        
        ### callTips
        self.setCallTipsVisible(0)
        self.setCallTipsPosition(QsciScintilla.CallTipsBelowText)
        self.setCallTipsStyle(QsciScintilla.CallTipsNoAutoCompletionContext)

        self.setMinimumSize(500, 400)

    ####################################
    def toggle_comments(self):
        lines = self.selected_lines()
        if len(lines) <= 0:
            return
        all_commented = True
        for line in lines:
            if not self.text(line).strip().startswith(self.comment_str):
                all_commented = False
        if not all_commented:
            self.comment_lines(lines)
        else:
            self.uncomment_lines(lines)

    def selections(self):
        regions = []
        for i in range(self.SendScintilla(QsciScintilla.SCI_GETSELECTIONS)):
            regions.append({
                'begin': self.SendScintilla(QsciScintilla.SCI_GETSELECTIONNSTART, i),
                'end': self.SendScintilla(QsciScintilla.SCI_GETSELECTIONNEND, i)
            })

        return regions

    def selected_lines(self):
        self.sel_regions = []
        all_lines = []
        regions = self.selections()
        for r in regions:
            start_line = self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, r['begin'])
            end_line = self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, r['end'])
            for cur_line in range(start_line, end_line + 1):
                if not cur_line in all_lines:
                    all_lines.append(cur_line)
            if r['begin'] <= r['end']:
                self.sel_regions.append(r)
        return all_lines

    def comment_lines(self, lines):
        indent = self.indentation(lines[0])
        for line in lines:
            indent = min(indent, self.indentation(line))
        self.beginUndoAction()
        for line in lines:
            self.adjust_selections(line, indent)
            self.insertAt(self.comment_str, line, indent)
        self.endUndoAction()
        self.restore_selections()

    def uncomment_lines(self, lines):
        self.beginUndoAction()
        for line in lines:
            line_start = self.SendScintilla(QsciScintilla.SCI_POSITIONFROMLINE, line)
            line_end = self.SendScintilla(QsciScintilla.SCI_GETLINEENDPOSITION, line)
            if line_start == line_end:
                continue
            if line_end - line_start < len(self.comment_str):
                continue
            done = False
            for c in range(line_start, line_end - len(self.comment_str) + 1):
                source_str = self.text(c, c + len(self.comment_str))
                if(source_str == self.comment_str):
                    self.SendScintilla(QsciScintilla.SCI_DELETERANGE, c, len(self.comment_str))
                    break
        self.endUndoAction()

    def restore_selections(self):
        if(len(self.sel_regions) > 0):
            first = True
            for r in self.sel_regions:
                if first:
                    self.SendScintilla(QsciScintilla.SCI_SETSELECTION, r['begin'], r['end'])
                    first = False
                else:
                    self.SendScintilla(QsciScintilla.SCI_ADDSELECTION, r['begin'], r['end'])

    def adjust_selections(self, line, indent):
        for r in self.sel_regions:
            if self.positionFromLineIndex(line, indent) <= r['begin']:
                r['begin'] += len(self.comment_str)
                r['end'] += len(self.comment_str)
            elif self.positionFromLineIndex(line, indent) < r['end']:
                r['end'] += len(self.comment_str)
    ####################################

    def on_margin_clicked(self, nmargin, nline, modifiers):
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
            self.parent.statusBar().showMessage("%s %s %s" % ("margin on line", nline, "removed"), 0)
            self.setSelection(nline, 0, nline + 1, 0)
            self.parent.removeBookmarkFromMarker(self.selectedText())
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)
            self.parent.statusBar().showMessage("%s %s" % ("added margin on line", nline), 0)
            self.setSelection(nline, 0, nline + 1, 0)
            self.parent.addBookmarkFromMarker(self.selectedText())

    def getSelectionFromEditor(self):
        line = self.getCursorPosition()[0] + 1
        pos = self.getCursorPosition()[1] 
        self.parent.lineLabel.setText("%s %s - %s %s" % ("line", line, "position", pos))

    ####################################################################

class myEditor(QMainWindow):
    def __init__(self, parent = None):
        super(myEditor, self).__init__(parent)
        self.words = []
        self.root = QFileInfo.path(QFileInfo(QCoreApplication.arguments()[0]))
        self.bookmarkslist = []
        print("self.root is: ", self.root)
        self.logo = os.path.join(self.root, "logo_128.png")
        self.appfolder = self.root
        self.openPath = ""
        self.statusBar().showMessage(self.appfolder)
        self.lineLabel = QLabel("line")
        self.statusBar().addPermanentWidget(self.lineLabel)
        self.MaxRecentFiles = 15
        self.windowList = []
        self.recentFileActs = []
        self.settings = QSettings("PyEdit", "PyEdit")
        self.dirpath = QDir.homePath() + "/Dokumente/python_files/"
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(QIcon(QPixmap(self.logo)))


        ### Editor Widget ...
        self.editor = QSC()
        self.editor.parent = self
        self.editor.textChanged.connect(self.editorChanged)
        if int(sys.version[0]) > 2:
            self.setStyleSheet(stylesheet2(self))
        self.extra_selections = []
        self.mainText = "#!/usr/bin/python3\n# -*- coding: utf-8 -*-\n"
        self.fname = ""
        self.filename = ""
        self.mypython = "2"
        self.shellWin = QTextEdit()
        self.shellWin.setContextMenuPolicy(Qt.CustomContextMenu)
        self.shellWin.setFixedHeight(90)

        self.createActions()
        ### Layout...
        layoutH = QHBoxLayout()
        layoutH.setSpacing(1.5)
        layoutH.addWidget(self.editor)
        ### systray
        self.createTrayIcon()
        self.trayIcon.show()
        ### statusbar
        self.statusBar()
        self.statusBar().showMessage('Welcome')
        ### begin toolbar
        tb = self.addToolBar("File")
        tb.setContextMenuPolicy(Qt.PreventContextMenu)
        tb.setIconSize(QSize(iconsize))
        tb.setMovable(False)
        tb.setAllowedAreas(Qt.AllToolBarAreas)
        tb.setFloatable(False)
       
        ### Manual
        self.manualAct = QAction("Manual", self, triggered = self.manual, shortcut = "F1")
        self.addAction(self.manualAct)
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
        self.commentAct1 = QAction("toggle Line comment", self, shortcut="F3",
        statusTip="toggle Line comment (F3)", triggered=self.commentLine)
        self.addAction(self.commentAct1)
                
        tb.addSeparator()           
        self.commentAct = QAction("toggle Line comment", self, shortcut="F2",
                statusTip="toggle Line comment (F2)", triggered=self.commentLine)
        self.commentAct.setIcon(QIcon.fromTheme(self.root + "/icons/comment"))
        tb.addAction(self.commentAct)
        
        ### color chooser
        tb.addSeparator()
        tb.addAction(QIcon.fromTheme(self.root + "/icons/color1"),"insert QColor", self.insertColor)
        tb.addSeparator()
        tb.addAction(QIcon.fromTheme("preferences-color"),"change Color", self.changeColor)    
        ###insert templates
        tb.addSeparator()
        self.templates = QComboBox()
        self.templates.setFixedWidth(120)
        self.templates.setToolTip("insert template")
        self.templates.activated[str].connect(self.insertTemplate)
        tb.addWidget(self.templates)
        ### path python buttons      
        tb.addSeparator()   
        self.py2Act = QAction("run in Python 2 (F4)", self, shortcut="F4",
                statusTip="run in Python 2 (F4)", triggered=self.runPy2)
        self.py2Act.setIcon(QIcon.fromTheme("python"))
        tb.addAction(self.py2Act)                               
        self.py3Act = QAction("run in Python 3.6 (F5)", self, shortcut="F5",
                statusTip="run in Python 3 (F5)", triggered=self.runPy3)
        self.py3Act.setIcon(QIcon.fromTheme(self.root + "/icons/python3"))
        tb.addAction(self.py3Act)
        tb.addSeparator()

        self.termAct = QAction("run in Terminal",
                statusTip="run in Terminal", triggered=self.runInTerminal)
        self.termAct.setIcon(QIcon.fromTheme("x-terminal-emulator"))
        tb.addAction(self.termAct)
        tb.addSeparator()

        tb.addAction(QIcon.fromTheme("edit-clear"),"clear Output Label", self.clearLabel)

        ### about buttons
        tb.addSeparator()
        tb.addAction(QIcon.fromTheme(self.root + "/icons/info2"),"&About PyEdit", self.about)
        tb.addAction(QAction(QIcon.fromTheme("process-stop"), "kill python", self, triggered=self.killPython))
        ### show / hide shellWin
        tb.addSeparator()
        self.shToggleAction = QAction("show/ hide shell window", self,
                statusTip="show/ hide shell window", triggered=self.handleShellWinToggle)
        self.shToggleAction.setIcon(QIcon.fromTheme("terminal"))
        self.shToggleAction.setCheckable(True)
        tb.addAction(self.shToggleAction) 

        ### thunar
        tb.addSeparator()
        self.fmanAction = QAction("open Filemanager", self,
                statusTip="open Filemanager", triggered=self.handleFM)
        self.fmanAction.setIcon(QIcon.fromTheme("file-manager"))
        tb.addAction(self.fmanAction)   
        ### TextEdit
        self.texteditAction = QAction("open selected Text in QTextEdit", self,
                statusTip="open selected Text in QTextEdit", triggered=self.handleTextEdit)
        self.texteditAction.setIcon(QIcon.fromTheme("text-editor"))
        tb.addAction(self.texteditAction)

        empty = QWidget()
        empty.setFixedWidth(18)
        tb.addWidget(empty)
        ### marker bookmarks
        self.bookmarksMarker = QComboBox()
        self.bookmarksMarker.setFixedWidth(280)
        self.bookmarksMarker.setToolTip("go to Marker bookmark")
        self.bookmarksMarker.activated[str].connect(self.gotoMarkerBookmark)
        tb.addWidget(self.bookmarksMarker)
        ## addStretch
        empty = QWidget();
        empty.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);
        tb.addWidget(empty)
        ### exit button
        self.exitAct = QAction("exit", self, shortcut=QKeySequence.Quit,
                statusTip="Exit", triggered=self.handleQuit)
        self.exitAct.setIcon(QIcon.fromTheme(self.root + "/icons/quit"))
        tb.addAction(self.exitAct)       
        ### end toolbar
        self.indentAct = QAction(QIcon.fromTheme(self.root + "/icons/format-indent-more"), "indent more", 
                                    self, triggered = self.indentLine, shortcut = "F8")
        self.indentLessAct = QAction(QIcon.fromTheme(self.root + "/icons/format-indent-less"), "indent less", 
                                    self, triggered = self.indentLessLine, shortcut = "F9")
        ### find / replace toolbar
        self.addToolBarBreak()
        tbf = self.addToolBar("Find")
        tbf.setContextMenuPolicy(Qt.PreventContextMenu)
        tbf.setMovable(False)
        tbf.setIconSize(QSize(iconsize))
        self.findfield = QLineEdit()
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
        self.repAllAct.setIcon(QIcon.fromTheme("gtk-find-and-replace"))
        self.repAllAct.setStatusTip("replace all")
        self.repAllAct.clicked.connect(self.replaceAll)
        tbf.addWidget(self.repAllAct)
        tbf.addSeparator()
        tbf.addAction(self.indentAct)
        tbf.addAction(self.indentLessAct)
        tbf.addSeparator()
        self.gotofield = QLineEdit()
        self.gotofield.addAction(QIcon.fromTheme("next"), QLineEdit.LeadingPosition)
        self.gotofield.setClearButtonEnabled(True)
        self.gotofield.setFixedWidth(120)
        self.gotofield.setPlaceholderText("go to line")
        self.gotofield.setToolTip("press RETURN to go to line")
        self.gotofield.returnPressed.connect(self.gotoLine)
        tbf.addWidget(self.gotofield)
        
        tbf.addSeparator() 
        self.bookmarks = QComboBox()
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
        tbf.addAction(QAction(QIcon.fromTheme("document-properties"), "check && reindent Text", 
                                self, triggered=self.reindentText))
        
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
        self.clearRecentAct = QAction("clear Recent Files List", self, triggered=self.clearRecentFiles)
        self.clearRecentAct.setIcon(QIcon.fromTheme("edit-clear"))
        self.filemenu.addAction(self.clearRecentAct)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.exitAct)
        
        editmenu = bar.addMenu("Edit")
        editmenu.addAction(QAction(QIcon.fromTheme('edit-undo'), "Undo", self, 
                                    triggered = self.editor.undo, shortcut = "Ctrl+u"))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-redo'), "Redo", self, 
                            triggered = self.editor.redo, shortcut = "Shift+Ctrl+u"))
        editmenu.addSeparator()
        editmenu.addAction(QAction(QIcon.fromTheme('edit-copy'), "Copy", self, 
                            triggered = self.editor.copy, shortcut = "Ctrl+c"))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-cut'), "Cut", self, 
                            triggered = self.editor.cut, shortcut = "Ctrl+x"))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-paste'), "Paste", self, 
                                    triggered = self.editor.paste, shortcut = "Ctrl+v"))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-delete'), "Delete", self, 
                                    triggered = self.editor.cut, shortcut = "Del"))
        editmenu.addSeparator()
        editmenu.addAction(QAction(QIcon.fromTheme('edit-select-all'), "Select All", self, 
                            triggered = self.editor.selectAll, shortcut = "Ctrl+a"))
        editmenu.addSeparator()
        editmenu.addAction(self.commentAct)
        editmenu.addSeparator()
        editmenu.addAction(self.py2Act)
        editmenu.addAction(self.py3Act)
        editmenu.addSeparator()
        editmenu.addAction(self.jumpToAct)
        editmenu.addSeparator()
        editmenu.addAction(self.indentAct)
        editmenu.addAction(self.indentLessAct)

        layoutV.addLayout(layoutH)
        self.shellWin.setMinimumHeight(28)
        self.shellWin.setStyleSheet(stylesheet2(self))
        self.shellWin.customContextMenuRequested.connect(self.shellWincontextMenuRequested)
        layoutV.addWidget(self.shellWin)
        ### main window
        mq = QWidget(self)
        mq.setLayout(layoutV)
        self.setCentralWidget(mq)
        
        self.editor.setFocus()
        self.editor.setText(self.mainText)
        self.editor.textChanged.connect(self.setWindowModified)
        
        ### Brackets ExtraSelection ...
        self.left_selected_bracket  = QTextEdit.ExtraSelection()
        self.right_selected_bracket = QTextEdit.ExtraSelection()
        
        ### shell settings
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(lambda: self.shellWin.append("starting shell"))
        self.process.finished.connect(lambda: self.shellWin.append("shell ended"))

        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.contextMenuRequested)
        
        self.loadTemplates()   
        self.readSettings()
        self.statusBar().showMessage("self.root is: " + self.root, 0)
        self.editor.setCursorPosition(self.editor.text().count('\n'), 0)
        self.setModified(False)
        
    def manual(self):
        self.infobox("Manual", Manual.manual_text)
        
    def editorChanged(self):
        if not self.filename == "":
            t = self.strippedName(self.filename)
            self.setWindowTitle("%s%s" % (t, "*"))

    def runInTerminal(self):
        print("running in terminal")
        if self.editor.text() == "":
            self.statusBar().showMessage("no Code!")
            return
        if not self.editor.text() == self.mainText:
            if self.filename:
                self.statusBar().showMessage("running " + self.filename + " in Lua")
                self.fileSave()
                self.shellWin.clear()
                dname = QFileInfo(self.filename).filePath().replace(QFileInfo(self.filename).fileName(), "")
                cmd = str('xfce4-terminal -e "python3 ' + dname + self.strippedName(self.filename) + '"')
                self.statusBar().showMessage(str(dname))
                QProcess().execute("cd '" + dname + "'")
                print(cmd)
                self.process.start(cmd)
            else:
                self.filename = "/tmp/tmp.py"
                self.fileSave()
                self.runInTerminal()
        else:
            self.statusBar().showMessage("no code to run")

    def handleShellWinToggle(self):
        if self.shellWin.isVisible():
            self.shellWin.setVisible(False)
        else:
            self.shellWin.setVisible(True)


    def handleFM(self):
        if "/" in self.shellWin.textCursor().selectedText():
            QProcess.startDetached("thunar", [self.shellWin.selectedText()])
        else:
            QProcess.startDetached("thunar", [os.path.dirname(self.filename)])

    def handleTextEdit(self):
        dir = os.path.dirname(sys.argv[0])
        filename = "QTextEdit.py"
        text = self.editor.selectedText()
        f = os.path.join(dir, filename)
        cmd = f + " '" + text + "'"
        print(cmd)
        QProcess.startDetached(f, [text])

    def killPython(self):
        if int(sys.version[0]) < 3:
            os.system("killall python")
        else:
            os.system("killall python3")

    def keyPressEvent(self, event):
        if  self.editor.hasFocus():
            if event.key() == Qt.Key_F10:
                self.findNextWord()
        
    def textColor(self):
        col = QColorDialog.getColor(QColor("#" + self.editor.selectedText()), self)
        self.pix.fill(col)
        if not col.isValid():
            return
        else:
            colorname = 'QColor("' + col.name() + '")'
            self.editor.insert(colorname)
            self.pix.fill(col)
        
    def loadTemplates(self):
        folder = self.appfolder + "/templates"
        if QDir().exists(folder):
            self.currentDir = QDir(folder)
            count = self.currentDir.count()
            fileName = "*"
            files = self.currentDir.entryList([fileName],
                    QDir.Files | QDir.NoSymLinks)

            for i in range(len(files)):
                file = (files[i])
                if file.endswith(".txt"):
                    self.templates.addItem(file.replace(self.appfolder + "/templates", "").replace(".txt", ""))
        
    def Test(self):
        self.editor.selectAll()
        
    def reindentText(self):
        if self.editor.text() == "" or self.editor.text() == self.mainText:
            self.statusBar().showMessage("no code to reindent")
        else:
            self.editor.selectAll()
            tab = "\t"
            oldtext = self.editor.selectedText()
            newtext = oldtext.replace(tab, "    ")
            self.editor.insert(newtext)    
            self.statusBar().showMessage("code reindented")

    def insertColor(self):
        col = QColorDialog.getColor(QColor("#000000"), self)
        if not col.isValid():
            return
        else:
            colorname = 'QColor("' + col.name() + '")'
            self.editor.insert(colorname)
            
    def changeColor(self):
        if not self.editor.selectedText() == "":
            col = QColorDialog.getColor(QColor("#" + self.editor.selectedText()), self)
            if not col.isValid():
                return
            else:
                colorname = col.name()
                self.editor.replaceSelectedText(colorname.replace("#", ""))
        else:
            col = QColorDialog.getColor(QColor("black"), self)
            if not col.isValid():
                return
            else:
                colorname = col.name()
                self.editor.insert(colorname)

    ### QPlainTextEdit contextMenu
    def contextMenuRequested(self, point):
        cmenu = QMenu()
        cmenu = self.editor.createStandardContextMenu()
        cmenu.addSeparator()
        cmenu.addAction(self.jumpToAct)
        cmenu.addSeparator()
        if not self.editor.selectedText() == "":
            cmenu.addAction(QIcon.fromTheme("gtk-find-and-replace"),"replace all occurrences with", self.replaceThis)
            cmenu.addSeparator()
        cmenu.addAction(QIcon.fromTheme("zeal"),"show help with 'zeal'", self.showZeal)
        cmenu.addAction(QIcon.fromTheme("firefox"),"find with 'firefox'", self.findWithFirefox)
        cmenu.addAction(QIcon.fromTheme("gtk-find-"),"find this (F10)", self.findNextWord)
        cmenu.addAction(self.texteditAction)
        cmenu.addSeparator()
        cmenu.addAction(self.py2Act)
        cmenu.addAction(self.py3Act)
        cmenu.addSeparator()
        cmenu.addAction(self.commentAct)
        cmenu.addSeparator()
        if not self.editor.selectedText() == "":
            cmenu.addAction(self.indentAct)
            cmenu.addAction(self.indentLessAct)       
        cmenu.addSeparator()
        cmenu.addAction(QIcon.fromTheme("preferences-color"),"insert QColor", self.insertColor)

        cmenu.addSeparator()
        cmenu.addAction(QIcon.fromTheme("preferences-color"),"change Color", self.changeColor)
        cmenu.exec_(self.editor.mapToGlobal(point))    

    ### shellWin contextMenu
    def shellWincontextMenuRequested(self, point):
        shellWinMenu = QMenu()
        shellWinMenu = self.shellWin.createStandardContextMenu()
        shellWinMenu.addSeparator()
        shellWinMenu.addAction(QIcon.fromTheme("zeal"),"show help with 'zeal'", self.showZeal_shell)
        shellWinMenu.addAction(QIcon.fromTheme("firefox"),"find with 'firefox'", self.findWithFirefox_shell)
        if "/" in self.shellWin.textCursor().selectedText():
            shellWinMenu.addAction(self.fmanAction)
        shellWinMenu.exec_(self.shellWin.mapToGlobal(point))   
        
    def replaceThis(self):
        rtext = self.editor.selectedText()
        text = QInputDialog.getText(self, "replace with","replace '" + rtext + "' with:", QLineEdit.Normal, "")
        oldtext = self.editor.text()
        if not (text[0] == ""):
            newtext = oldtext.replace(rtext, text[0])
            self.editor.setText(newtext)
            self.setModified(True)

    def showZeal(self):
        if self.editor.selectedText() == "":
            rtext = self.editor.wordAtLineIndex(self.editor.getCursorPosition()[0], self.editor.getCursorPosition()[1])
            print(rtext)
        else:
            rtext = self.editor.selectedText() ##.replace(".", "::")
        cmd = "zeal " + str(rtext)
        QProcess().startDetached(cmd)

    def findWithFirefox(self):
        if self.editor.selectedText() == "":
            rtext = self.editor.wordAtLineIndex(self.editor.getCursorPosition()[0], self.editor.getCursorPosition()[1])
        else:
            rtext = "python%20" + self.editor.selectedText().replace(" ", "%20")
        url = "https://www.google.com/search?q=" +  rtext
        QDesktopServices.openUrl(QUrl(url))

    def showZeal_shell(self):
        if not self.shellWin.selectedText() == "":
            rtext = self.shellWin.selectedText()
            cmd = "zeal " + str(rtext)
            QProcess().startDetached(cmd)

    def findWithFirefox_shell(self):
        if not self.shellWin.selectedText() == "":
            rtext = "python%20" + self.shellWin.selectedText().replace(" ", "%20")
            url = "https://www.google.com/search?q=" +  rtext.replace(" ", "%20")
            QDesktopServices.openUrl(QUrl(url))
   
    def findNextWord(self):
        if self.editor.selectedText() == "":
            rtext = self.editor.wordAtLineIndex(self.editor.getCursorPosition()[0], self.editor.getCursorPosition()[1])
        else:
            rtext = self.editor.selectedText()
        self.findfield.setText(rtext)
        self.findText()

    def indentLine(self):
        if not self.editor.selectedText() == "":
            newline = "\n"
            ot = self.editor.selectedText()
            self.editor.removeSelectedText() 
            theList  = ot.splitlines()
            newlist = ["    " + suit for suit in theList]
            newtext = newline.join(newlist)
            self.editor.insert(newtext)
            self.setModified(True)   
            self.editor.findFirst(newtext, True, True, True, True)
            self.statusBar().showMessage("more indented")
        
    def indentLessLine(self):
        if not self.editor.selectedText() == "":
            newline = "\n"
            ot = self.editor.selectedText()
            self.editor.removeSelectedText() 
            theList  = ot.splitlines()
            newlist = [suit.replace("    ", "", 1) for suit in theList]
            newtext = newline.join(newlist)
            self.editor.insert(newtext)
            self.setModified(True)   
            self.editor.findFirst(newtext, True, True, True, True)
            self.statusBar().showMessage("less indented")
        
    def dataReady(self):
        t = ""
        out = ""
        try:
            out = str(self.process.readAll(), encoding = 'utf8').rstrip()
        except TypeError:
            self.msgbox("Error", str(self.process.readAll(), encoding = 'utf8'))
            out = str(self.process.readAll()).rstrip()
            self.shellWin.moveCursor(self.cursor.Start) ### changed
        self.shellWin.append(out)    
        if "line" in out:
            t = out.rpartition(", line ")[2].partition(",")[0]
            self.gotoErrorLine(t)
        else:
            print("no tr", t)
        self.shellWin.moveCursor(QTextCursor.End)
        self.shellWin.ensureCursorVisible()
        
    def createActions(self):
        for i in range(self.MaxRecentFiles):
            self.recentFileActs.append(
                   QAction(self, visible=False,
                            triggered=self.openRecentFile))
            
    def addBookmark(self):
        linenumber = self.getLineNumber()
        linetext = self.editor.block().text().strip()
        self.bookmarks.addItem(linetext, linenumber)

    def addBookmarkFromMarker(self, linetext):
        linenumber = self.getLineNumber()
        self.bookmarksMarker.addItem(linetext.replace("\n", ""), linenumber)

    def removeBookmarkFromMarker(self, linetext):
        linenumber = self.getLineNumber()
        ind = self.bookmarksMarker.findText(linetext.replace("\n", ""))
        self.bookmarksMarker.removeItem(ind)
        
    def getLineNumber(self):
        linenumber = self.editor.getCursorPosition()[0] + 1
        return linenumber
            
    def gotoLine(self):
        ln = int(self.gotofield.text())
        if len(self.editor.contractedFolds()) > 0:
            self.editor.clearFolds()
        self.editor.setCursorPosition(ln - 1, 1)
        self.editor.setFirstVisibleLine(ln - 2)
        self.editor.setFocus()
        
    def gotoErrorLine(self, ln):
        t = int(ln)
        if t != 0:
            self.editor.setCursorPosition(t - 1, 0)
            self.editor.setFirstVisibleLine(t - 1)
        else:
            return
            
    def gotoMarkerBookmark(self):
        ln = self.bookmarksMarker.itemData(self.bookmarksMarker.currentIndex()) ###self.getLineNumber()
        self.editor.setCursorPosition(ln - 2, 0)
        self.editor.setFirstVisibleLine(ln - 3)
        self.editor.setFocus()        
        
    def gotoBookmark(self):
        btext = self.bookmarks.itemText(self.bookmarks.currentIndex())
        btext = btext.partition("(")[0]
        self.editor.findFirst(btext, True, True, True, True)
        ln = self.getLineNumber()
        self.editor.setCursorPosition(ln - 1, 0)
        self.editor.setFirstVisibleLine(ln - 2)
        self.editor.setFocus()
        
    def gotoBookmarkFromMenu(self):
        if self.editor.selectedText() == "":
            rtext = self.editor.wordAtLineIndex(self.editor.getCursorPosition()[0], 
                                                self.editor.getCursorPosition()[1])
        else:
            rtext = self.editor.selectedText()
        toFind = rtext
        self.bookmarks.setCurrentIndex(0)
        if self.bookmarks.findText(toFind, Qt.MatchExactly):
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
        if not self.editor.text() == "":
            self.clearBookmarks()
            newline = "\n"
            fr = "from"
            im = "import"
            d = "def"
            d2 = "    def"
            c = "class"
            sn = str("if __name__ ==")
            line = ""
            list = []
            ot = self.editor.text()
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

                self.bookmarkslist = [self.bookmarks.itemText(i) for i in range(self.bookmarks.count())]
                self.bookmarkslist = [w.replace('    ', '') for w in self.bookmarkslist]
                self.bookmarkslist.sort()
                self.bookmarks.clear()
                self.bookmarks.addItems(self.bookmarkslist)
                
        self.statusBar().showMessage("bookmarks changed")
                
    def clearLabel(self):
        self.shellWin.setText("")
            
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
            self.editor.setText(self.mainText)
            self.filename = ""
            self.editor.setCursorPosition(self.editor.text().count('\n'), 0)
            self.setModified(False)
            self.statusBar().showMessage("new File created.")
            self.editor.setFocus()
            self.bookmarks.clear()
            self.setWindowTitle("new File[*]")
            
       ### open File
    def openFileOnStart(self, path=None):
        if path:
            self.openPath = QFileInfo(path).path() ### store path for next time
            inFile = QFile(path)
            if inFile.open(QFile.ReadWrite | QFile.Text):
                text = inFile.readAll()
                try:
                        # Python v3.
                    text = str(text, encoding = 'utf8')
                except TypeError:
                        # Python v2.
                    text = str(text)
                self.editor.setText(text.replace(tab, "    "))
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
                outstr << self.editor.text()
                QApplication.restoreOverrideCursor()  
                self.statusBar().showMessage("File '" + path 
                                            + "' loaded succesfully & bookmarks added & backup created ('" 
                                            + self.filename + "_backup" + "')")
        
        ### open File
    def openFile(self, path=None):
        if self.openPath == "":
            self.openPath = self.dirpath
        if self.maybeSave():
            if not path:
                path, _ = QFileDialog.getOpenFileName(self, "Open File", self.openPath,
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
            outstr << self.editor.text()
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
        title = "about PyEdit3"
        message = """
                    <span style='color: #3465a4; font-size: 24pt;font-weight: bold;'
                    >PyEdit3</strong></span></p><h2>Python Editor</h2>created by  
                    <h3><a title='Axel Schneider' href='http://goodoldsongs.jimdo.com' target='_blank'>
                    Axel Schneider</a><br> with PyQt5 & QScintilla<br><br></h3>
                    <span style='color: #555753; font-size: 9pt;'>©2019 Axel Schneider</strong></span></p>
                        """
        self.infobox(title, message)
        
    def runPy3(self):
        if self.editor.text() == "":
            self.statusBar().showMessage("no Code!")
            return
        if not self.editor.text() == self.mainText:
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
        if self.editor.text() == "":
            self.statusBar().showMessage("no Code!")
            return
        if not self.editor.text() == self.mainText:
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
        self.shellWin.clear()
        dname = QFileInfo(self.filename).filePath().replace(QFileInfo(self.filename).fileName(), "")
        self.statusBar().showMessage(str(dname))
        QProcess().execute("cd '" + dname + "'")
        self.process.start(cmd,['-u', dname + self.strippedName(self.filename)])
            
    def commentLine(self):
        self.editor.toggle_comments()
        
    def findText(self):
        word = self.findfield.text()
        if self.editor.findFirst(word, True, False, True, True):
            linenumber = self.getLineNumber()
            self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
        else:
            self.statusBar().showMessage("<b>'" + self.findfield.text() + "'</b> not found")
            self.editor.getCursorPosition(0, 0)            
            if self.editor.findFirst(word):
                linenumber = self.getLineNumber()
                self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
            
    def findBookmark(self, word):
        if self.editor.findFirst(word):
            linenumber = self.getLineNumber() 
            self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
            
    def handleQuit(self):
        if self.maybeSave():
            print("Goodbye ...")
            app.quit()

    def document(self):
        return self.editor.document
        
    def isModified(self):
        return self.editor.isModified()

    def setModified(self, modified):
        self.editor.setModified(modified)

    def setWindowModified(self):
        self.editor.setModified(True)

    def setLineWrapMode(self, mode):
        self.editor.setLineWrapMode(mode)

    def clear(self):
        self.editor.clear()

    def setPlainText(self, *args, **kwargs):
        self.editor.setText(*args, **kwargs)

    def setDocumentTitle(self, *args, **kwargs):
        self.editor.setDocumentTitle(*args, **kwargs)

    def set_number_bar_visible(self, value):
        self.numbers.setVisible(value)
        
    def replaceAll(self):
        if not self.editor.text() == "":
            if not self.findfield.text() == "":
                self.statusBar().showMessage("replacing all")
                oldtext = self.editor.text()
                newtext = oldtext.replace(self.findfield.text(), self.replacefield.text())
                self.editor.setText(newtext)
                self.setModified(True)
            else:
                self.statusBar().showMessage("nothing to replace")
        else:
                self.statusBar().showMessage("no text")
        
    def replaceOne(self):
        if not self.editor.text() == "":
            if not self.findfield.text() == "":
                self.statusBar().showMessage("replacing all")
                oldtext = self.editor.text()
                newtext = oldtext.replace(self.findfield.text(), self.replacefield.text(), 1)
                self.editor.setText(newtext)
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
        if self.settings.contains('recentFileList'):
            mytext = ""
            files = self.settings.value('recentFileList', [])
            if not len(files) == 0:
                numRecentFiles = len(files)
        
                for i in range(numRecentFiles):
                    text = "&%d %s" % (i + 1, self.strippedName(files[i]))
                    self.recentFileActs[i].setText(text)
                    self.recentFileActs[i].setData(files[i])
                    self.recentFileActs[i].setVisible(True)
                    self.recentFileActs[i].setIcon(QIcon.fromTheme("gnome-mime-text-x-python"))
        
                for j in range(numRecentFiles, self.MaxRecentFiles):
                    self.recentFileActs[j].setVisible(False)
        
                self.separatorAct.setVisible((numRecentFiles > 0))
            else:
                for i in range(len(self.recentFileActs)):
                    self.recentFileActs[i].remove()
        
    def strippedName(self, fullFileName):
        return QFileInfo(fullFileName).fileName()
        
    def clearRecentFiles(self):
        self.settings.remove('recentFileList')
        self.recentFileActs = []
        self.settings.sync()
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, myEditor):
                widget.updateRecentFileActions()
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
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, 
                    self, Qt.Dialog|Qt.NoDropShadowWindowHint).show()        
        
    def insertTemplate(self):
        line = int(self.getLineNumber())
        path = self.appfolder + "/templates/" + self.templates.itemText(self.templates.currentIndex()) + ".txt"
        if path:
            inFile = QFile(path)
            if inFile.open(QFile.ReadOnly | QFile.Text):
                text = inFile.readAll()
                self.editor.setFocus()
                try: ### python 3
                    self.editor.insert(str(text, encoding = 'utf8'))
                except TypeError:  ### python 2
                    self.editor.insert(str(text))
                self.setModified(True)
                self.findBookmarks()
                self.statusBar().showMessage("'" + self.templates.itemText(self.templates.currentIndex()) 
                                            + "' inserted")
                inFile.close()
                text = ""
                self.selectLine(line)
            else:
                self.statusBar().showMessage("error loadind Template")
            
    def selectLine(self, line):
        return
        
    def createTrayIcon(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Systray",
                    "I couldn't detect any system tray on this system.")
        else:
            self.trayIcon = QSystemTrayIcon(self)
            self.trayIcon.setIcon(QIcon(QPixmap(self.logo)))
            self.trayIconMenu = QMenu(self)
            self.trayIconMenu.addAction(QAction(QIcon.fromTheme("applications-python"), "about PyEdit", 
                                        self, triggered=self.about))
            self.trayIconMenu.addSeparator()
            self.trayIconMenu.addAction(QAction(QIcon.fromTheme("application-exit"),"Exit", 
                                        self, triggered=self.handleQuit))
            self.trayIcon.setContextMenu(self.trayIconMenu)
                       
  
def stylesheet2(self):
    return """
QTextEdit
{
background: #2e3436;
color: #729fcf;
font-family: Monospace;
font-size: 8pt;
padding-left: 6px;
border: 1px solid #1EAE3D;
}
QStatusBar
{
font-family: Noto Sans;
color: #204a87;
font-size: 8pt;
}
QLabel
{
font-family: Noto Sans;
color: #204a87;
font-size: 8pt;
}
QLineEdit
{
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
    stop: 0 #E1E1E1, stop: 0.4 #e5e5e5,
    stop: 0.5 #e9e9e9, stop: 1.0 #d2d2d2);
font-family: Helvetica;
font-size: 8pt;
}
QPushButton
{
background: #D8D8D8;
font-family: Noto Sans;
font-size: 8pt;
}
QComboBox
{
background: #D8D8D8;
font-family: Noto Sans;
font-size: 8pt;
}
QMenuBar
{
font-family: Noto Sans;
font-size: 8pt;
border: 0px;
}
QMenu
{
font-family: Noto Sans;
font-size: 8pt;
}
QToolBar
{
border: 0px;
background: transparent;
}
QMainWindow
{
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
    stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
    stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
}
    """       

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = myEditor()
    win.setWindowTitle("PyEdit" + "[*]")
    win.show()
    if len(sys.argv) > 1:
        print(sys.argv[1])
        win.openFileOnStart(sys.argv[1])

    sys.exit(app.exec_())
