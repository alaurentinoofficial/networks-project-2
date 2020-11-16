from models.player import Player
from models.response import Response
from models.request import Request
from constants import codes

class GameController():
    def __init__(self, db):
        self.db = db
    
    def register(self, request: Request):
        ip, port = request.connection
        p = Player(ip, port)

        if len(self.db["players"]) == 5:
            return Response(code=codes.SUCCESS, body="The game is full, await some minutes")
        elif (p in self.db["players"]):
            return Response(code=codes.SUCCESS, body="you're already registred")
        
        # Add into a virtual database
        self.db["players"].append(p)

        print("[*] Player Registred!", str(p))

        return Response(code=codes.SUCCESS, body="ok")