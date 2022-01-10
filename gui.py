from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QApplication, QMessageBox, QDockWidget, QLabel, QMessageBox, QSpacerItem, QHBoxLayout, QMainWindow, QSpacerItem, QVBoxLayout, QWidget, QPushButton, QComboBox
from PySide2.QtCore import QDir, QFile, QTextStream, QTimer, QSize
from PySide2.QtGui import QIcon, QPicture, QPixmap, QFont
import sys
import os
from backend import CODE_LENGTH, MAX_TRIES, COLORS, Token, Game
from BreezeStyleSheets import breeze_resources

# Useful parameters
ICONS_DIR = 'Icons/'
EMPTY_TOKEN_ICON_PATH = 'grey'
ROW_GAP = 100
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 100
SECRET_ICON = 'secret'

class TokenSelection(QComboBox):
    icons = []
    def __init__(self, position, parent):
        super().__init__()
        self.position = position
        self.parent = parent
        if not TokenSelection.icons:
            TokenSelection.initIcons()
        for icon in TokenSelection.icons:
            self.addItem(icon, '')
        self.currentIndexChanged.connect(lambda: self.parent.currentRow().setTokenColor(self.position, COLORS[self.currentIndex()]))
    
    @staticmethod
    def initIcons():
        TokenSelection.icons = []
        for c in COLORS:
            iconPath = ICONS_DIR + c + '.svg'
            if os.path.exists(iconPath):
                TokenSelection.icons.append(QIcon(iconPath))

class SelectionRow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QHBoxLayout()
        self.tokenSelectionRow = []
        for i in range(CODE_LENGTH):
            tokenSelection = TokenSelection(i, self.parent)
            self.tokenSelectionRow.append(tokenSelection)
            self.layout.addWidget(tokenSelection)

        self.setLayout(self.layout)

    def getCode(self):
        code = []
        for t in self.tokenSelectionRow:
            code.append(COLORS[t.currentIndex()])
        return(code)
    
    def checkCompleteness(self):
        """Checks if all the tokens are defined"""
        complete = True
        if 0 in [token.currentIndex() for token in self.tokenSelectionRow]:
            complete = False
            self.parent.alert("You must define the color of all tokens before submitting")
        return(complete)

class TokenRow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        emptyTokenIcon = QPixmap(ICONS_DIR + EMPTY_TOKEN_ICON_PATH + '.svg')
        self.tokens = []
        dimensions = QSize(40, 40)
        for i in range(CODE_LENGTH):
            emptyToken = QLabel()
            emptyToken.setFixedSize(dimensions)
            self.tokens.append(emptyToken)
            emptyToken.setPixmap(emptyTokenIcon)
            self.layout.addWidget(emptyToken)
        self.setLayout(self.layout)
    
    def setTokenColor(self, tokenIndex, color):
        colorPath = ICONS_DIR + color + '.svg'
        self.tokens[tokenIndex].setPixmap(QPixmap(colorPath))

class SecretRow(TokenRow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._hidden = False
        self.hideCode()
    
    def hideCode(self):
        if not self._hidden:
            secretIcon = QPixmap(ICONS_DIR + SECRET_ICON + '.svg')
            for t in self.tokens:
                t.setPixmap(secretIcon)
            self._hidden = True

    def revealCode(self):
        if self._hidden:
            for t, color in zip(self.tokens, self.parent.game.code):
                icon = QPixmap(ICONS_DIR + color + '.svg')
                t.setPixmap(icon)
            self._hidden = False

    

class ScoreRow(TokenRow):
    def __init__(self):
        super().__init__()

class BoardRow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.addWidget(TokenRow())
        self.layout.addSpacerItem(QSpacerItem(ROW_GAP, 0))
        self.layout.addWidget(ScoreRow())
        self.setLayout(self.layout)

class ScorePanel(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Score")
        self.body = QWidget()
        self.layout = QVBoxLayout()
        self.rows = []
        for i in range(MAX_TRIES):
            row = TokenRow()
            self.rows.append(row)
            self.layout.addWidget(row)
        self.layout.addSpacerItem(QSpacerItem(0, 72))
        self.body.setLayout(self.layout)
        self.setWidget(self.body)

    @property
    def currentRowIdx(self):
        if self.parent.game:
            return(self.parent.game.tries)

    def showScore(self, index, score):
        for i in range(score.white):
            self.rows[index].setTokenColor(i, Token.WHITE.value)
        for i in range(score.white, score.black + score.white):
            self.rows[index].setTokenColor(i, Token.BLACK.value)
       
class GameControls(QDockWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.body = QWidget()
        self.setWidget(self.body)
        self.layout = QVBoxLayout()
        self.startBtn = QPushButton(QIcon(ICONS_DIR + 'start.svg'), '')
        self.submitBtn = QPushButton(QIcon(ICONS_DIR + 'submit.svg'), '')
        self.resignBtn = QPushButton(QIcon(ICONS_DIR + 'resign.svg'), '')

        # formatting buttons
        buttonSize = QSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.startBtn.setFixedSize(buttonSize)
        self.submitBtn.setFixedSize(buttonSize)
        self.resignBtn.setFixedSize(buttonSize)


        # connecting buttons
        self.startBtn.clicked.connect(self.parent.startGame)
        self.resignBtn.clicked.connect(self.parent.resign)

        self.layout.addWidget(self.startBtn)
        self.layout.addWidget(self.submitBtn)
        self.layout.addWidget(self.resignBtn)

        # self.layout.addSpacerItem(QSpacerItem(0, 800))
        self.body.setLayout(self.layout)

class Console(QDockWidget):
    def __init__(self):
        super().__init__()
        self.body = QLabel()
        self.setWidget(self.body)
        self.printMsg("Welcome to MasterMind !")

    def printMsg(self, msg):
        if not(isinstance(msg, str)):
            msg = str(msg)
        self.body.setText(msg)

class GameGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = None
        self.setWindowTitle("MasterMind")
        self.setWindowIcon(QIcon(ICONS_DIR + 'brain.svg'))
        self.body = QWidget()
        self.setCentralWidget(self.body)
        self.scorePanel = ScorePanel()
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.scorePanel)
        self.controlPanel = GameControls(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.controlPanel)
        self.console = Console()
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.console)
        self.scorePanel.show()
        self.secretRow = SecretRow(self)
        self.selectionRow = SelectionRow(self)
        self.rows = []
        # initializing rows
        for i in range(MAX_TRIES):
            self.rows.append(TokenRow())
        # self.currentRowIdx = 0

    @property
    def currentRowIdx(self):
        if self.game:
            return(self.game.tries)  

    def currentRow(self):
        return(self.rows[self.currentRowIdx])    

    def alert(self, msg):
        """Prints an alert message in a pop-up window"""
        alert = QMessageBox()
        if not(isinstance(msg, str)):
            msg = str(msg)
        alert.setText(msg)
        alert.exec()  

    def log(self, msg):
        self.console.printMsg(msg)

    def startGame(self):
        self.resetBoard()
        self.game = Game(self)
        self.selectionRow.show()
        self.controlPanel.submitBtn.clicked.connect(self.submit)
        self.secretRow.hideCode()

    def resign(self):
        if self.game:
            self.game.lost()
            self.secretRow.revealCode()
            self.selectionRow.hide()

    def submit(self):
        if self.selectionRow.checkCompleteness():
            code = self.selectionRow.getCode()
            score = self.game.submit(code)
            self.scorePanel.showScore(self.currentRowIdx - 1, score)    

            # checking if game is won
            if self.game.iswon or self.game.islost:
                self.selectionRow.hide()
                self.secretRow.revealCode()
            
            else:
                for token, color in zip(self.currentRow().tokens, code):
                    icon = QPixmap(ICONS_DIR + color + '.svg')
                    token.setPixmap(icon)

    def resetBoard(self):
        for tokenRow, scoreRow in zip(self.rows, self.scorePanel.rows):
            for i in range(CODE_LENGTH):
                tokenRow.setTokenColor(i, COLORS[0])
                scoreRow.setTokenColor(i, COLORS[0])


class GameLayout(GameGui):
    def __init__(self):
        super().__init__()
        # window dimensions     
        # self.resize(1600, 900)
        self.layout = QVBoxLayout()

        self.body.setLayout(self.layout)
        self.layout.addSpacerItem(QSpacerItem(0, 60))
        for row in self.rows:
            self.layout.addWidget(row)
        self.layout.addWidget(self.secretRow)
        self.layout.addWidget(self.selectionRow)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0 , 0)
        self.selectionRow.hide()
 
app = QApplication([])
font = QFont("Century Gothic", 10)
app.setFont(font)
# set stylesheet
file = QFile(":/dark.qss")
file.open(QFile.ReadOnly | QFile.Text)
stream = QTextStream(file)
app.setStyleSheet(stream.readAll())

game = GameLayout()
game.show()
app.exec_()

