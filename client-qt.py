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

running = False

def await_reponse(socket, textbox, buttons, main):
        global running
        socket.settimeout(1) 
        while running:
            try:
                data, client_conn = socket.recvfrom(2048)
                result = json.loads(data.decode())

                print(data)

                if result.get("code"):
                    if result.get("code") == codes.FULL:
                        textbox.setText("\nThe run is full!\nWait and try again")
                        main.exit.setEnabled(True)
                        main.replay.setEnabled(True)
                        main.replay.setText("Try again")
                    if result.get("code") == codes.IS_RUNNING:
                        textbox.setText("\nThe gamming is running!\nWait some minutes and try again!")
                        main.exit.setEnabled(True)
                        main.replay.setEnabled(True)
                        main.replay.setText("Try again")
                    elif result.get("code") == codes.REGISTRED:
                        textbox.setText("Resgistred!\n\n Wait for more players...")
                    
                    elif result.get("code") == codes.QUESTION:
                        msg = result["body"]["question"] + "\r\n"

                        textbox.setText(msg)

                        used_alterantives = []
                        for alternative in result["body"]["alternatives"]:
                            btn = buttons.get(alternative["code"])

                            if btn:
                                used_alterantives.append(alternative["code"])
                                btn.setText("\n" + alternative["text"])
                                btn.setEnabled(True)

                        for k, v in buttons.items():
                            if k not in used_alterantives:
                                v.setText("")
                                v.setEnabled(False)
                    
                    elif result.get("code") == codes.FINISH_ROUND:
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

                        msg = "Scores\n\n"

                        for pos, (name, points) in enumerate(players):
                            msg += "{0}º) \t {1} \t {2} points\n".format(pos+1, name, points)
                        
                        textbox.setText(msg)
                        main.exit.setEnabled(True)
                        main.replay.setEnabled(True)
                        main.replay.setText("Replay")
                        running =False
                        break
            except timeout: 
                continue
            except (KeyboardInterrupt, SystemExit):
                break

@pyqtSlot()
def on_click(socket, answer, buttons, label):
    def wrapped():
        obj = {"body": {"answer": answer}, "method": "ADD", "route": "/answer"}
        socket.sendto(json.dumps(obj).encode(), ("localhost", 9000))

        for k, v in buttons.items():
            v.setEnabled(False)

        label.setText("Wating server response...")

        return
    
    return wrapped

def replay_event(main, setReplay):
    def wrapped():
        setReplay(True)
        main.close()
    
    return wrapped

if __name__ == '__main__':
    replay = False
    running = False
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
    
    def setReplay(x):
            global replay
            print("aqui")
            print(replay)
            replay = x
            print(replay)

    main.exit.clicked.connect(MainWindow.close)
    main.replay.clicked.connect(replay_event(MainWindow, setReplay))

    dlg = NicknameDlg(None)
    if dlg.exec_():
        nickname = dlg.ui.lineEdit.text()

        while True:
            replay = False
            running = True
            receive_thread = Thread(target=await_reponse, args=(sock, main.label, buttons, main,))
            receive_thread.start()

            main.exit.setEnabled(False)
            main.replay.setEnabled(False)

            payload = {"body": {"nickname": nickname}, "method": "ADD", "route": "/register"}
            msg = json.dumps(payload).encode()
            
            sock.sendto(msg, ("localhost", 9000))
            try:
                MainWindow.show()
                sys.exit(app.exec_())
            except:
                running = False
                receive_thread.join()

                print(replay)

                if replay:
                    continue
                else:
                    break