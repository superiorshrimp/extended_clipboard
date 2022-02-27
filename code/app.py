from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from config import *
from datetime import datetime as dt
import qdarkstyle

class ListWidgetItem(QListWidgetItem):
    def __init__(self):
        super().__init__()
        self.date = dt.now()
    def __lt__(self, other):
        return self.date > other.date
    def __le__(self, other):
        return self.date >= other.date
    def __eq__(self, other):
        return self.date == other.date
    def __gt__(self, other):
        return self.date < other.date
    def __ge__(self, other):
        return self.date <= other.date

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('logo.png'))
        self.setStyleSheet(qdarkstyle.load_stylesheet())
        self.setWindowTitle("qxcb")
        font = QFont("Calibri", 8)
        font.setStyleHint(QFont.Monospace)
        QApplication.setFont(font)
        self.mode, self.width, self.height = loadConfig()
        self.resize(self.width, self.height)
        self.setMinimumSize(300, 450)
        self.content = []
        main = QWidget(self)
        self.setCentralWidget(main)
        mainLayout = QVBoxLayout()
        main.setLayout(mainLayout)
        
        self.searchBar = QLineEdit()
        self.searchBar.textChanged.connect(self.lineEditChanged)
        self.sortCombobox = QComboBox()
        self.QList = QListWidget()
        self.QList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.QList.setDragDropMode(QAbstractItemView.InternalMove)
        
        header = self.createHeaderLayout()
        bottom = self.createBottomLayout()
        
        self.mergeMainLayout(mainLayout, header, bottom)
        self.QList.setFocus()
        
        self.createShortcuts()
        QApplication.clipboard().dataChanged.connect(self.clipboardChanged)
        
    def resizeEvent(self, event):
        w = self.frameGeometry().width()
        h = self.frameGeometry().height()
        updateConfig(self.mode, w, h)
        self.width = w
        self.height = h  

    def pushFrontItem(self, value): #unless...
        item = ListWidgetItem()
        self.content.append([value, item.date])
        item.setText(value)
        if self.sortCombobox.currentIndex() == 0:
            self.QList.insertItem(0, item)
        else:
            self.QList.addItem(item)
    
    def pushFrontItemOldDate(self, value, date):
        item = ListWidgetItem()
        item.date = date
        item.setText(value)
        if self.sortCombobox.currentIndex() == 0:
            self.QList.insertItem(0, item)
        else:
            self.QList.addItem(item)
  
    def paste(self):
        text = QApplication.clipboard().text()
        self.pushFrontItem(text)
    
    def clipboardChanged(self):
        if self.mode == 1:
            text = QApplication.clipboard().text()
            self.pushFrontItem(text)
    
    def modeChanged(self):
        self.mode = (self.mode + 1) % 2
        updateConfig(self.mode, self.width, self.height)

    def enterPressed(self):
        if self.mode == 0 and self.QList.hasFocus():
            QApplication.clipboard().setText(self.QList.currentItem().text())

    def delPressed(self):
        self.removeSelected()

    def clearAll(self):
        self.QList.clear()
        self.content.clear()

    def selectAll(self):
        self.QList.selectAll()

    def createHeaderLayout(self):
        header = QWidget()
        headerLayout = QGridLayout()
        header.setLayout(headerLayout)
        
        self.sortCombobox.addItem("most recent first")
        self.sortCombobox.addItem("oldest first")
        self.sortCombobox.activated.connect(self.reverse)
        
        modeCheckbox = QCheckBox("autocopy mode")
        if self.mode == 1:
            modeCheckbox.setChecked(True)
        modeCheckbox.stateChanged.connect(self.modeChanged)
        
        headerLayout.addWidget(self.searchBar, 0, 0)
        headerLayout.addWidget(self.sortCombobox, 0, 1)
        headerLayout.addWidget(modeCheckbox, 0, 2)
        
        return header
    
        pass
    
    def createBottomLayout(self):
        bottom = QWidget()
        bottomLayout = QGridLayout()
        bottom.setLayout(bottomLayout)
        
        clearAllButton = QPushButton("clear all")
        clearAllButton.clicked.connect(self.clearAll)
        bottomLayout.addWidget(clearAllButton, 0, 0)
        
        removeSelectedButton = QPushButton("remove selected")
        removeSelectedButton.clicked.connect(self.removeSelected)
        bottomLayout.addWidget(removeSelectedButton, 0, 1)
        
        return bottom
    
    def createShortcuts(self):
        enterShortcut = QShortcut(QKeySequence('Return'), self) #enter
        enterShortcut.activated.connect(self.enterPressed)
        
        delShortcut = QShortcut('Del', self) #delete selected
        delShortcut.activated.connect(self.removeSelected)
        
        ctrlcShortcut = QShortcut(QKeySequence('Ctrl+C'), self)
        ctrlcShortcut.activated.connect(self.enterPressed) #same effect as enter
        
        ctrlvShortcut = QShortcut(QKeySequence('Ctrl+V'), self)
        ctrlvShortcut.activated.connect(self.paste)
        
        ctrlaShortcut = QShortcut(QKeySequence('Ctrl+V'), self)
        ctrlaShortcut.activated.connect(self.selectAll)

    def mergeMainLayout(self, mainLayout, header, bottom):
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0,0,0,0)
        
        mainLayout.addWidget(header)
        mainLayout.addWidget(self.QList)
        mainLayout.addWidget(bottom)
        
        mainLayout.setStretchFactor(header, 0)
        mainLayout.setStretchFactor(self.QList, 1)
        mainLayout.setStretchFactor(bottom, 0)
        
        return mainLayout

    def reverse(self):
        if self.sortCombobox.currentIndex() == 0:
            self.QList.sortItems(Qt.AscendingOrder)
        else:
            self.QList.sortItems(Qt.DescendingOrder)
    
    def removeSelected(self):
        for el in reversed(sorted(self.QList.selectedIndexes())):
            for i in range(len(self.content)):
                if self.content[i][0] == el:
                    del self.content[i]
            self.QList.takeItem(el.row())
                       
    def lineEditChanged(self):
        text = self.searchBar.text()
        self.find(text)
    
    def find(self, text):
        self.QList.clear()
        found = [self.content[i] for i in range(len(self.content)) if text in self.content[i][0]]
        for el in found:
            self.pushFrontItemOldDate(el[0], el[1])
    
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()