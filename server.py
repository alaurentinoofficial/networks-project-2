import json
from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM

from models.router import Router
from models.response import Response
from models.request import Request
from constants import codes

class ServerUDP:
    def __init__(self, address, port, router=Router()):
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind((address, port))
        self.router = router

    def start(self):
        while True:
            data, client_conn = self.server_socket.recvfrom(2048)

            Thread(target=self.open_connection, args=(self.server_socket, client_conn, data, self.router)).start()

    @staticmethod
    def open_connection(socket, client_conn, data, router):
        request = None
        
        try:
            payload = json.loads(data)
            request = Request(**payload)
            request.connection = client_conn

            try:
                socket.sendto(router.resolve(request).encode(), client_conn)
            except Exception as e:
                socket.sendto(Response(code=codes.INTERNAL_ERROR, body=str(e)).encode(), client_conn)
        except Exception as e:
            socket.sendto(Response(code=codes.BAD_REQUEST, body=str(e)).encode(), client_conn)