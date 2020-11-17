import json
from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM, timeout

from models.router import Router
from models.response import Response
from models.request import Request
from constants import codes

class ServerUDP(Thread):
    def __init__(self, connection, router=Router()):
        Thread.__init__(self)

        self.connection = connection
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(connection)
        self.router = router
        self.__running__ = False

    def send(self, response: Response, connection):
        self.server_socket.sendto(response.encode(), connection)

    def run(self):
        self.__running__ = True
        self.server_socket.settimeout(1) 

        while self.__running__:
            try:
                data, client_conn = self.server_socket.recvfrom(2048)
            except timeout: 
                continue
            except (KeyboardInterrupt, SystemExit):
                self.__running__ = False
                break

            Thread(target=self.open_connection, args=(self.server_socket, client_conn, data, self.router)).start()

    def stop(self):
        self.__running__ = False

    @staticmethod
    def open_connection(socket, client_conn, data, router):
        request = None
        
        try:
            payload = json.loads(data)
            request = Request(**payload)
            request.connection = client_conn

            try:
                response = router.resolve(request)

                if response != None:
                    socket.sendto(response.encode(), client_conn)
            except Exception as e:
                print(e)
                socket.sendto(Response(code=codes.INTERNAL_ERROR, body="Internal error").encode(), client_conn)
        except Exception as e:
            print(e)
            socket.sendto(Response(code=codes.BAD_REQUEST, body="Invalid request").encode(), client_conn)