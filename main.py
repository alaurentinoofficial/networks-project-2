import time
import json
import random

from server import ServerUDP
from models.router import Router
from controllers.game_controller import GameController 

NUM_PLAYERS = 5 
ROUND_TIME = 5 # seconds

db = {"players": []}

if __name__ == "__main__":
    router = Router()
    router.add("/register", GameController(db).register, "ADD") # {"body": null, "method": "ADD", "route": "/register"}

    ServerUDP('localhost', 8081, router).start()

