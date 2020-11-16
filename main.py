import time
import json
import random

from server import ServerUDP
from models.router import Router
from controllers.game_controller import GameController 

NUM_PLAYERS = 5 
ROUND_TIME = 5 # seconds

def load_json(filename="questions.json", encoding="utf-8"):
    config = {}
    with open(filename, encoding=encoding) as file:
        config = json.load(file)
    
    return config

def random_sort(list_obj):
    list_obj = list_obj[:]
    random.shuffle(list_obj)

    return list_obj

db = {"players": []}

if __name__ == "__main__":
    router = Router()
    router.add("/register", GameController(db).register, "ADD") # {"body": null, "method": "ADD", "route": "/register"}

    ServerUDP('localhost', 8081, router).start()

