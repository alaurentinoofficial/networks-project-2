import time
import json
import random

from server import ServerUDP
from models.router import Router
from models.room import Room, Question, Alternative
from models.response import Response
from utils.load_questions import load_json, random_sort
from controllers.game_controller import GameController 

NUM_PLAYERS = 5 
ROUND_TIME = 5 # seconds

db = {"players": []}

if __name__ == "__main__":
    try:
        questions = load_json()

        new_questions = []
        for obj in questions:
            obj["alternatives"] = [Alternative(**a) for a in obj["alternatives"]]
            new_questions.append(Question(**obj))

        room = Room(questions=new_questions, max_players=NUM_PLAYERS)

        # --

        server = ServerUDP(('localhost', 8081,))
        game_controller = GameController(room)

        server.router.add("/register", game_controller.register, "ADD") # {"body": null, "method": "ADD", "route": "/register"}
        server.router.add("/answer", game_controller.answer, "ADD")

        server.start()

        # --
        
        while len(room.players) != 1:
            print(".")
            time.sleep(1)
        
        for i_round, question in enumerate(random_sort(room.questions)):
            for p in room.players:
                result = {}
                result["question"] = question.text
                result["alternatives"] = [a.__dict__ for a in question.alternatives]
                server.send(Response(0, result), (p.ip, p.port,))
            
            time.sleep(5)
    
    except (KeyboardInterrupt, SystemExit):
        pass

server.stop()