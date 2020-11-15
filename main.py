import time
import json
import random

from server import ServerUDP, Router, Route

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

def print_request(request):
    print(request)

    return "Ok".encode()

if __name__ == "__main__":
    router = Router()
    router.add(Route("/register", print_request, "POST")) # {"route": "/register", "body": null, "method": "POST"}

    ServerUDP('localhost', 8080, router).serve()

