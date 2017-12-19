import sys

from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
    
            ### highlighter
class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)
        
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("#2C2CC8"))
        keywordFormat.setFontWeight(QFont.Bold)

        keywordPatterns = ["\\bdef\\b","\\bimport\\b","\\bchar\\b", "\\bclass\\b", "\\bconst\\b",
                "\\bdouble\\b", "\\belif\\b", "\\benum\\b", "\\bexplicit\\b", "\\bfriend\\b",
                "\\bif\\b", "\\binline\\b", "\\bint\\b", "\\blong\\b", "\\bnamespace\\b",
                "\\boperator\\b", "\\bprivate\\b", "\\bprotected\\b",
                "\\bpublic\\b", "\\bshort\\b", "\\bsignals\\b", "\\bsigned\\b",
                "\\bslots\\b", "\\bstatic\\b", "\\bstruct\\b",
                "\\btemplate\\b", "\\btypedef\\b", "\\btypename\\b",
                "\\bunion\\b", "\\bunsigned\\b", "\\bvirtual\\b", "\\bvoid\\b",
                "\\bvolatile\\b"]

        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                for pattern in keywordPatterns]
            
        booleanFormat = QTextCharFormat()
        booleanFormat.setFontWeight(QFont.Bold)
        booleanFormat.setForeground(QColor("#D63030"))
        self.highlightingRules.append((QRegExp("\\b[False]+\\b"),
                booleanFormat))
        self.highlightingRules.append((QRegExp("\\b[True]+\\b"),
                booleanFormat))

        classFormat = QTextCharFormat()
        classFormat.setFontWeight(QFont.Bold)
        classFormat.setForeground(QColor("#3F3F3F"))
        self.highlightingRules.append((QRegExp("\\bQ[A-Za-z]+\\b"),
                classFormat))
        self.highlightingRules.append((QRegExp("\\b[self]+\\b"),
                classFormat))

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(QColor("#90701B"))
        self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))
        
        squotationFormat = QTextCharFormat()
        squotationFormat.setForeground(QColor("#90701B"))
        self.highlightingRules.append((QRegExp("\'.*\'"), squotationFormat))

        functionFormat = QTextCharFormat()
#        functionFormat.setFontItalic(True)
        functionFormat.setForeground(QColor.fromRgb(200,44,44))
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\()"),
                functionFormat))
            
        green = "#4A9243"
            
        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setForeground(QColor(green))
        self.highlightingRules.append((QRegExp("#[^\n]*"),
                singleLineCommentFormat))

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QColor(green))

        self.commentStartExpression = QRegExp("/\\*")
        self.commentEndExpression = QRegExp("\\*/")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength,
                    self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text,
                    startIndex + commentLength);