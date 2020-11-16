from models.player import Player
from models.response import Response
from models.request import Request
from constants import codes

class GameController():
    def __init__(self, db):
        self.db = db
    
    def register(self, request: Request):
        # Create new player
        ip, port = request.connection
        p = Player(ip, port)

        # Add into a virtual database
        self.db["players"].append(p)

        print("[*] Player Registred!", str(p))

        return Response(code=codes.SUCCESS, body="ok")