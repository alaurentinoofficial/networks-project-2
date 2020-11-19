import time
from typing import List

from models.room import Room, Alternative, Question
from server import ServerUDP

from utils.load_questions import load_json, random_sort

if __name__ == "__main__":
    questions = []
    for obj in load_json():
        obj["alternatives"] = [Alternative(**a) for a in obj["alternatives"]]
        questions.append(Question(**obj))

    server = ServerUDP(('localhost', 9000,))
    room = Room(socket=server.server_socket,questions=questions, max_players=1)

    try:
        server.router.add("/register", room.register, "ADD")
        server.router.add("/answer", room.answer, "ADD")

        server.start()
        room.start()
    
        while room.running:
            pass
    except:
        pass

    if room:
        room.stop()

    if server:    
        server.stop()