from models.player import Player
from models.room import Room
from models.response import Response
from models.request import Request
from constants import codes

class GameController():
    def __init__(self, room: Room):
        self.room = room
    
    def register(self, request: Request):
        ip, port = request.connection
        p = Player(ip, port)

        if len(self.room.players) == self.room.max_players:
            return Response(code=codes.SUCCESS, body="the game is full, await some minutes")
        elif (p in self.room.players):
            return Response(code=codes.SUCCESS, body="you're already registred")
        
        # Add into a virtual database
        self.room.players.append(p)

        print("[*] Player Registred!", str(p))

        return Response(code=codes.SUCCESS, body="ok")
    
    def answer(self, request: Request):
        ip, port = request.connection
        p = Player(ip, port)

        if type(request.body) is {}:
            value = request.body.get("answer")

            if value != None and p in self.room.players:
                if value == question.correct_alternative:
                    p.points += 1
                
                question.answers.append(Answer(value, id_player=f"{ip}:{port}", game_round=i_round))