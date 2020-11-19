import sys
import json

import constants.codes as codes

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

from ui.main import Ui_MainWindow
from ui.nickname import Ui_Dialog, NicknameDlg

from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM, timeout

def await_reponse(socket, textbox, buttons, running):
        socket.settimeout(1) 

        while running():
            try:
                data, client_conn = socket.recvfrom(2048)
                result = json.loads(data.decode())

                print(data)

                if result.get("code"):
                    if result.get("code") == codes.REGISTRED:
                        textbox.setText("Resgistred!\n\n Wait for more players...")
                    
                    elif result.get("code") == codes.QUESTION:
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
                        textbox.setText(result["body"])

                        for k, v in buttons.items():
                            v.setText("")
                            v.setEnabled(False)
                    
                    elif result.get("code") == codes.RESULT_RANK:
                        players = list(result["body"].items())
                        players.sort(key=lambda x: x[1], reverse=True)

                        for k, v in buttons.items():
                            v.setText("")
                            v.setEnabled(False)

                        msg = ""

                        for pos, (name, points) in enumerate(players):
                            msg += "{0}º) {1} - {2} points\n".format(pos+1, name, points)
                        
                        textbox.setText(msg)
            except timeout: 
                continue
            except (KeyboardInterrupt, SystemExit):
                break

@pyqtSlot()
def on_click(socket, answer, buttons, label):
    def wrapped():
        obj = {"body": {"answer": answer}, "method": "ADD", "route": "/answer"}
        socket.sendto(json.dumps(obj).encode(), ("localhost", 8081))

        for k, v in buttons.items():
            v.setEnabled(False)

        label.setText("Wating server response...")

        return
    
    return wrapped

if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_DGRAM)

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    main = Ui_MainWindow()
    main.setupUi(MainWindow)

    buttons = {
        "a": main.button_a,
        "b": main.button_b,
        "c": main.button_c,
        "d": main.button_d,
        "e": main.button_e,
        "f": main.button_f,
        "g": main.button_g,
        "h": main.button_h
    }

    main.label.setText("Wait...")

    for k, v in buttons.items():
        v.setText("")
        v.setEnabled(False)
        v.clicked.connect(on_click(sock, k, buttons, main.label))

    dlg = NicknameDlg(None)
    if dlg.exec_():
        nickname = dlg.ui.lineEdit.text()

        running = True
        receive_thread = Thread(target=await_reponse, args=(sock, main.label, buttons, lambda: running,))
        receive_thread.start()

        payload = {"body": {"nickname": nickname}, "method": "ADD", "route": "/register"}
        msg = json.dumps(payload).encode()
        
        sock.sendto(msg, ("localhost", 8081))

        try:
            MainWindow.show()
            sys.exit(app.exec_())
        except:
            running = False