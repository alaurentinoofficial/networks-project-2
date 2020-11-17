from socket import socket, AF_INET, SOCK_DGRAM, timeout
from threading import Thread

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('localhost', 45743,))

running = False

def await_reponse(socket):
    running = True
    socket.settimeout(1) 

    while running:
        try:
            data, client_conn = socket.recvfrom(2048)
            print("")
            print(data)
            print("")
        except timeout: 
            continue
        except (KeyboardInterrupt, SystemExit):
            self.__running__ = False
            break

t = Thread(target=await_reponse, args=(sock,))
t.start()

try:
    while True:
        mensagem = input() # {"body": null, "method": "ADD", "route": "/register"}
        sock.sendto(mensagem.encode(), ('localhost', 8081))
except (KeyboardInterrupt, SystemExit):
    running = False

sock.close()
