import sys
import json

import constants.codes as codes

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM, timeout

  
class App(QMainWindow):
    def __init__(self, socket):
        super().__init__()
        self.title = 'Quiz Game'
        self.left = 50
        self.top = 50
        self.width = 460
        self.height = 410
        self.socket = socket
        self.initUI()
        self.register()
        self.receive_thread = Thread(target=self.await_reponse, args=(socket, self.label, self.buttons, self.show,))
        self.receive_thread.start()

    @staticmethod
    def await_reponse(socket, textbox, buttons, app):
        running = True
        socket.settimeout(1) 

        while running:
            try:
                data, client_conn = socket.recvfrom(2048)
                result = json.loads(data.decode())

                print(data)

                if result.get("code"):
                    if result.get("code") == codes.QUESTION:
                        msg = result["body"]["question"] + "\r\n"

                        textbox.setText(msg)

                        used_alterantives = []
                        for alternative in result["body"]["alternatives"]:
                            btn = buttons.get(alternative["code"])

                            if btn:
                                used_alterantives.append(alternative["code"])
                                btn.setText(alternative["text"])
                                btn.setEnabled(True)

                        for k, v in buttons.items():
                            if k not in used_alterantives:
                                v.setText("")
                                v.setEnabled(False)
                    
                    elif result.get("code") == codes.AWAIT_NEXT_QUESTION:
                        textbox.setText("Await 5 seconds for next question!\nGet ready!")

                        for k, v in buttons.items():
                            v.setText("")
                            v.setEnabled(False)
                    
                    elif result.get("code") == codes.RESULT_RANK:
                        players = list(result["body"].items())
                        players.sort(key=lambda x: x[1], reverse=True)

                        msg = ""

                        for pos, (name, points) in enumerate(players):
                            msg += "{0}º) {1} - {2} points".format(pos+1, name, points)
                        
                        textbox.setText(msg)
            except timeout: 
                continue
            except (KeyboardInterrupt, SystemExit):
                self.__running__ = False
                break
    
    def register(self):
        self.socket.sendto('{"body": {"nickname": "Jimmy"}, "method": "ADD", "route": "/register"}'.encode(), ("localhost", 8081))
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create the question label
        self.label = QLabel('Awaiting players...', self)
        self.label.move(10, 10)
        self.label.setFixedSize(440, 250)
        self.label.setWordWrap(True)

        group_x = 250

        self.button_a = QPushButton('A', self)
        self.button_a.resize(200,40)
        self.button_a.move(20,group_x)
        self.button_a.setEnabled(False)

        self.button_b = QPushButton('B', self)
        self.button_b.resize(200,40)
        self.button_b.move(240,group_x)
        self.button_b.setEnabled(False)

        self.button_c = QPushButton('C', self)
        self.button_c.resize(200,40)
        self.button_c.move(20,group_x + 50)
        self.button_c.setEnabled(False)

        self.button_d = QPushButton('D', self)
        self.button_d.resize(200,40)
        self.button_d.move(240,group_x + 50)
        self.button_d.setEnabled(False)

        self.button_e = QPushButton('E', self)
        self.button_e.resize(200,40)
        self.button_e.move(20,group_x + 100)
        self.button_e.setEnabled(False)

        self.button_f = QPushButton('F', self)
        self.button_f.resize(200,40)
        self.button_f.move(240,group_x + 100)
        self.button_f.setEnabled(False)

        self.buttons = {
            "a": self.button_a,
            "b": self.button_b,
            "c": self.button_c,
            "d": self.button_d,
            "e": self.button_e,
            "f": self.button_f
        }

        for k, v in self.buttons.items():
            v.clicked.connect(self.on_click(k, self.buttons, self.label))
        
        self.show()
    
    @pyqtSlot()
    def on_click(self, answer, buttons, label):
        def wrapped():
            obj = {"body": {"answer": answer}, "method": "ADD", "route": "/answer"}
            self.socket.sendto(json.dumps(obj).encode(), ("localhost", 8081))

            for k, v in buttons.items():
                v.setEnabled(False)

            label.setText("Aguradando apuração do servidor...")

            return
        
        return wrapped


if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('localhost', 45743,))

    app = QApplication(sys.argv)
    ex = App(sock)
    sys.exit(app.exec_())
    