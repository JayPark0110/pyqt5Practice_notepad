import sys
from typing import Pattern
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QTextCursor
from PyQt5 import QtCore

form_class = uic.loadUiType("14. notepad_searchDirection\\notepad.ui")[0]

class findWindow(QDialog):
    def __init__(self, parent): # 부모 윈도우(메모장)가 있기 때문에 parent 적어주기
        super(findWindow, self).__init__(parent)
        uic.loadUi("14. notepad_searchDirection\\find.ui", self)
        self.show()

        self.parent = parent
        self.cursor = parent.plainTextEdit.textCursor()
        self.pe = parent.plainTextEdit
        
        self.pushButton_findnext.clicked.connect(self.findNext)
        self.pushButton_cancel.clicked.connect(self.close)

        self.radioButton_down.clicked.connect(self.updown_radio_button)
        self.radioButton_up.clicked.connect(self.updown_radio_button)
        self.up_down = "down"

    def updown_radio_button(self):
        if self.radioButton_up.isChecked():
            self.up_down = "up"
            #print("up")
        elif self.radioButton_down.isChecked():
            self.up_down = "down"
            #print("down")
        
    def keyReleaseEvent(self, event):
        if self.lineEdit.text():
            self.pushButton_findnext.setEnabled(True)
        else:
            self.pushButton_findnext.setEnabled(False)
    
    def findNext(self):
        pattern = self.lineEdit.text()
        text = self.pe.toPlainText()
        self.cursor = self.parent.plainTextEdit.textCursor()    # 이 줄을 다시 가져옴

        reg = QtCore.QRegExp(pattern)
        
        if self.checkBox_CaseSensitive.isChecked(): # 대/소문자 구분
            cs = QtCore.Qt.CaseSensitive    # 구분
        else:
            cs = QtCore.Qt.CaseInsensitive  # 미구분
        
        reg.setCaseSensitivity(cs)
        
        pos = self.cursor.position()
        
        if self.up_down =='down':
            index = reg.indexIn(text, pos)    # 검색하기, 0번에서 시작하기
        else:
            pos -= len(pattern) + 1    # 역방향 검색 반복을 위해서 커서를 검색한 패턴 앞으로 옮기는 것(+1) 오류가 존재하기는 함.
            index = reg.lastIndexIn(text, pos)  # 역방향 검색 ! 근데 한번만 찾음..;        

        if (index != -1) and (pos > -1): # 검색된 결과가 있다면
            self.setCursor(index, len(pattern)+index)
        else:
            self.notFoundMsg(pattern)

    def notFoundMsg(self, pattern):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('메모장')
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText('\"{}\"을(를) 찾을 수 없습니다.'.format(pattern))
        msgBox.addButton('확인', QMessageBox.YesRole)   # 0
        msgBox.exec()

    def setCursor(self, start, end):    # 블럭지정(start, end)
        self.cursor.setPosition(start)  # 앞에 커서를 찍고
        self.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, end-start)  # 뒤로 커서를 움직인다
        self.pe.setTextCursor(self.cursor)


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.action_open.triggered.connect(self.openFunction)
        self.action_save.triggered.connect(self.saveFunction)
        self.action_saveas.triggered.connect(self.saveAsFunction)
        self.action_close.triggered.connect(self.close)
        
        self.action_undo.triggered.connect(self.undoFucntion)
        self.action_cut.triggered.connect(self.cutFunction)
        self.action_copy.triggered.connect(self.copyFunction)
        self.action_paste.triggered.connect(self.pasteFunction)

        self.action_find.triggered.connect(self.findFunction)


        self.opened = False
        self.opened_file_path = '제목 없음'

    def save_changed_data(self):
        msgBox = QMessageBox()
        msgBox.setText("변경 내용을 {}에 저장하시겠습니까?".format(self.opened_file_path))
        msgBox.addButton('저장', QMessageBox.YesRole)   # 0
        msgBox.addButton('저장 안 함', QMessageBox. NoRole) # 1        
        msgBox.addButton('취소', QMessageBox.RejectRole)    # 2
        ret = msgBox.exec()
        
        if ret == 0:
            self.saveFunction()
        else:
            return ret

    def ischanged(self):
        if not self.opened: # 열린 적은 없는데
            if self.plainTextEdit.toPlainText().strip():    # 데이터 변경사항있으면 True
                return True
            return False

        current_data = self.plainTextEdit.toPlainText() # 현재 데이터
        # 파일에 저장된 데이터
        with open(self.opened_file_path, encoding='UTF8') as f:
                file_data = f.read()

        if current_data == file_data:   # 열린적이 있고 변경사항 체크 
            return False    # 변경사항 없으면 
        else:
            return True     # 변경사항 있으면 


    def closeEvent(self, event):
        if self.ischanged():  # 열린 적이 있고 변경사항이 있으면 저장
            ret = self.save_changed_data()       
        
            if ret == 2:
                event.ignore()        

    def save_file(self, fname):
        data = self.plainTextEdit.toPlainText()
        with open(fname, 'w', encoding='UTF8') as f:
            f.write(data)
        
        self.opened = True
        self.opened_file_path = fname

        print("save {}!!" .format(fname))

    def open_file(self, fname):
        with open(fname, encoding='UTF8') as f:
                data = f.read()
        self.plainTextEdit.setPlainText(data)
                    
        self.opened = True
        self.opened_file_path = fname

        print("open {}!!" .format(fname))
    
    def openFunction(self):
        if self.ischanged():  # 열린 적이 있고 변경사항이 있으면 저장
            ret = self.save_changed_data()

        fname = QFileDialog.getOpenFileName(self)
        if fname[0]:    # 예외 처리
            self.open_file(fname[0])

    def saveFunction(self):
        if self.opened:
            self.save_file(self.opened_file_path)
        else:
            self.saveAsFunction()

    def saveAsFunction(self):
        fname = QFileDialog.getSaveFileName(self)
        if fname[0]:    # 예외 처리
            self.save_file(fname[0])


    def undoFucntion(self):
        self.plainTextEdit.undo()

    def cutFunction(self):
        self.plainTextEdit.cut()

    def copyFunction(self):
        self.plainTextEdit.copy()

    def pasteFunction(self):
        self.plainTextEdit.paste()

    def findFunction(self):
        findWindow(self)        

app = QApplication(sys.argv)
mainWindow = WindowClass()
mainWindow.show()

app.exec_()