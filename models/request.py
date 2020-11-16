import json
from typing import Tuple
from utils.methods_validator import validate_methods
from models.encoder import Encoder

class Request(Encoder):
    route: str
    body: object
    connection: Tuple[str, int]

    def __init__(self, route: str, method: str, body: object, connection=None):
        if not validate_methods(method):
            raise ValueError("Method is invalid.\nValid options: GET, ADD, UPDATE, DELETE")

        self.route = route
        self.body = body
        self.method = method
        self.connection = connection
    
    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()