from typing import Callable
from utils.methods_validator import validate_methods
from models.encoder import Encoder
from models.response import Response
from models.request import Request
import constants.codes as codes

class Route:
    def __init__(self, route: str, callback: Callable[[Request], Response], *methods):
        self.route = route
        self.callback = callback
        self.methods = [m.upper() for m in methods if validate_methods(m)]

class Router:
    def __init__(self, routes = []):
        self.routes = routes
    
    def add(self, route, callback, *methods):
        self.routes.append(Route(route, callback, *methods))

    def resolve(self, request) -> Response:
        for route in self.routes:
            if route.route == request.route and request.method in route.methods:
                return route.callback(request)
        
        return Response(code=codes.NOT_FOUND, body=f"Not found {request.route}")
