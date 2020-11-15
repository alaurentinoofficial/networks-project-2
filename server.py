import json
from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM

class Request:
    def __init__(self, route, body, method, connection):
        self.route = route
        self.body = body
        self.method = method
        self.connection = connection
        

class Route:
    def __init__(self, route, callback, *methods):
        self.route = route
        self.callback = callback
        self.methods = [m.upper() for m in methods]

class Router:
    def __init__(self, routes = []):
        self.routes = routes
    
    def add(self, route):
        self.routes.append(route)

    def resolve(self, request: Request):
        for route in self.routes:
            print(route.route == request.route, route.route, request.route)
            print(request.method in route.methods, request.method, route.methods)
            if route.route == request.route and request.method in route.methods:
                return route.callback(request)
        
        return None

class ServerUDP:
    def __init__(self, address, port, router=Router()):
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind((address, port))
        self.router = router

    def serve(self):
        while True:
            data, client_conn = self.server_socket.recvfrom(2048)

            Thread(target=self.open_connection, args=(self.server_socket, client_conn, data, self.router)).start()

    @staticmethod
    def open_connection(socket, client_conn, data, router):
        print(client_conn, data, router)
        try:
            payload = json.loads(data)
            request = Request(
                route=payload["route"]
                , body=payload["body"]
                , method=payload["method"].upper()
                , connection=client_conn
            )

            socket.sendto(router.resolve(request), client_conn)
        except ValueError as e:
            print(e)
            socket.sendto(f"Invalid arguments: {data}".encode(), client_conn)