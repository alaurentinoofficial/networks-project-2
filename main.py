import time
import json
import random

from constants import codes
from server import ServerUDP
from models.router import Router
from models.room import Room, Question, Alternative, Answer
from models.player import Player
from models.response import Response
from models.request import Request
from utils.load_questions import load_json, random_sort
from controllers.game_controller import GameController 

NUM_PLAYERS = 2
ROUND_TIME = 10 # seconds

questions = load_json()

new_questions = []
for obj in questions:
    obj["alternatives"] = [Alternative(**a) for a in obj["alternatives"]]
    new_questions.append(Question(**obj))

room = Room(questions=new_questions, max_players=NUM_PLAYERS)
actual_question = None
already_won = False

def register(request: Request):
        ip, port = request.connection
        p = Player(ip, port)

        if len(room.players) == room.max_players:
            return Response(code=codes.INVALID_PARAMETERS, body="the game is full, await some minutes")
        elif (p in room.players):
            return Response(code=codes.INVALID_PARAMETERS, body="you're already registred")
        
        # Add into a virtual database
        room.players.append(p)

        print("[*] Player Registred!", str(p))

        return Response(code=codes.REGISTRED, body="ok")
    
def answer(request: Request):
    global already_won
    ip, port = request.connection

    print(ip, port)

    p = Player(ip, port)
    pp = None

    for player in room.players:
        print(p, player)
        if p == player:
            pp = player
            break

    if pp == None:
        return Response(codes.NOT_ALLOWED, body="You aren't in the room")

    if actual_question == None:
        return Response(codes.INVALID_PARAMETERS, body="Game isn't started")
    
    if already_won != None:
        return Response(code=codes.NOT_ALLOWED, body="Player already won")
    
    if isinstance(request.body, dict):
        value = request.body.get("answer")
        if value != None:
            if value == actual_question.correct_code:
                for pp in room.players:
                    if p == pp:
                        pp.point += 25

                already_won = pp
                return Response(code=codes.SUCCESS, body="Greate, you win this round")
            else:
                pp.point -= 5
                return Response(code=codes.INVALID_PARAMETERS, body="Wrong answer")
            
            actual_question.answered_players.append(pp)

if __name__ == "__main__":
    try:
        server = ServerUDP(('localhost', 8081,))
        game_controller = GameController(room)

        server.router.add("/register", register, "ADD")
        server.router.add("/answer", answer, "ADD")

        server.start()

        # --
        
        while len(room.players) != NUM_PLAYERS:
            print(".")
            time.sleep(1)
        
        for i_round, question in enumerate(random_sort(room.questions)):
            already_won = None
            actual_question = question
            start_time = time.time()
            
            for p in room.players:
                result = {}
                result["question"] = question.text
                result["alternatives"] = [a.__dict__ for a in question.alternatives]
                server.send(Response(codes.QUESTION, result), (p.ip, p.port,))

            while not already_won != None and (time.time() - start_time) <= ROUND_TIME:
                pass

            for i in range(len(room.players)):
                if not room.players[i] in actual_question.answered_players:
                    room.players[i].point -= 1
                else:
                    print(room.players[i], actual_question.answered_players)
            
            if i_round < len(room.questions) - 1:
                for p in room.players:
                    if p == already_won:
                        server.send(Response(codes.AWAIT_NEXT_QUESTION, "You won this round!\nWait 5 seconds!\nGet ready!"), (p.ip, p.port,))
                    else:
                        server.send(Response(codes.AWAIT_NEXT_QUESTION, "Wait 5 seconds!\nGet ready!"), (p.ip, p.port,))
            
            time.sleep(1)
        
        ranking = {f"{p.ip}:{p.port}": p.point for p in room.players}

        for p in room.players:
            server.send(Response(codes.RESULT_RANK, ranking), (p.ip, p.port,))

    except:
        pass

server.stop()