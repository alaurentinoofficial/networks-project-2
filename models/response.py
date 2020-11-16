import json
from models.encoder import Encoder

class Response(Encoder):
    code: int
    body: object

    def __init__(self, code: int, body: object):
        self.code = code
        self.body = body
    
    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()