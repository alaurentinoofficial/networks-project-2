import time
from typing import List
from threading import Thread

import constants.codes as codes

from models.request import Request
from models.response import Response
from models.player import Player
from models.room import Question, Alternative, Answer
from server import ServerUDP

from utils.load_questions import load_json, random_sort

class Room(Thread):
    questions: List[Question]
    players: List[Player]
    last_question: Question
    running: bool
    round_hit: bool
    max_players: int
    round_time: int

    def __init__(self, socket, questions: List[Question], max_players: int = 5, round_time: int = 10, players: List[Player] = []):
        super().__init__()
        self.questions = questions
        self.players = players
        self.last_question = None
        self.max_players = max_players
        self.running = False
        self.game_running = False
        self.round_hit = False
        self.socket = socket
        self.round_time = round_time

    def play(self):
        for q in self.questions:
            q.answers = []

        try:
            while len(self.players) != self.max_players and self.running:
                print(".")
                time.sleep(1)
            
            if not self.running:
                return
            
            self.game_running = True
            for i_round, question in enumerate(random_sort(self.questions)):
                self.round_hit = False
                
                if not self.running:
                    return

                self.last_question = question
                start_time = time.time()
                
                for p in self.players:
                    result = {"question": question.text, "alternatives": [a.__dict__ for a in question.alternatives]}
                    self.socket.sendto(Response(codes.QUESTION, result).encode(), (p.ip, p.port,))

                while not self.round_hit and (time.time() - start_time) <= self.round_time and len(self.last_question.answers) != len(self.players) and self.running:
                    pass

                if not self.running:
                    return

                for i in range(len(self.players)):
                    _exists = False
                    _won = False

                    for ans in self.last_question.answers:
                        if ans.player == self.players[i]:
                            _exists = True
                            _won = ans.correct
                            break
                    
                    if _won:
                        self.players[i].points += 25
                    elif _exists:
                        self.players[i].points -= 5
                    else:
                        self.players[i].points -= 1

                    if _won:
                        self.socket.sendto(
                            Response(
                                codes.FINISH_ROUND
                                , "\nYou won this round!\nWait 5 seconds!\nGet ready!"
                            ).encode()
                            , (self.players[i].ip, self.players[i].port,)
                        )
                    else:
                        self.socket.sendto(
                            Response(
                                codes.FINISH_ROUND
                                , "\nWait 5 seconds!\nGet ready!"
                            ).encode()
                            , (self.players[i].ip, self.players[i].port,)
                        )
                

                if i_round < len(self.questions) - 1:
                    time.sleep(5)
            
            ranking = {p.name: p.points for p in self.players}

            for p in self.players:
                self.socket.sendto(Response(codes.RESULT_RANK, ranking).encode(), (p.ip, p.port,))

            self.game_running = False
        except ValueError as e:
            print(e)

    def run(self):
        self.running = True
        while self.running:
            self.players = []
            self.game_running = False
            self.last_question = None

            self.play()
        
        self.game_running = False
        self.running = False
        
    def status(self, request: Request):
        return Response(code=codes.SUCCESS, body={"total": self.max_players, "actual": len(self.players), 'running': self.running})
    
    def register(self, request: Request):
        ip, port = request.connection

        if isinstance(request.body, dict):
            nickname = request.body.get("nickname")

            if nickname != None:
                player = Player(ip, port, nickname)

                # Block if the gamming is running
                if self.game_running or self.last_question != None:
                    return Response(code=codes.NOT_ALLOWED, body="Gamming is running")
                
                if len(self.players) == self.max_players:
                    return Response(code=codes.FULL, body="The room is full")

                # Check if user is not already registred
                elif player in self.players:
                    return Response(code=codes.ALREADY_EXISTS, body="Already exists")

                # Add new player
                print("[*] Player Registred!", str(player))
                self.players.append(player)
                return Response(code=codes.REGISTRED, body="OK")
        
        # Return invalid parameters
        return Response(code=codes.INVALID_PARAMETERS, body="Invalid params")
    
    def answer(self, request: Request):
        ip, port = request.connection
        p = Player(ip, port, "")
        result = [player for player in self.players if p == player]

        if len(result) == 0:
            return Response(code=codes.NOT_ALLOWED, body="You aren't in this room")
            
        elif not self.running and self.last_question == None:
            return Response(code=codes.NOT_RUNNING, body="Game ins't started yet")
        
        elif self.round_hit:
            return Response(code=codes.ALREADY_EXISTS, body="Someone alrady won")

        player = result[0]
        for ans in self.last_question.answers:
            if ans.player == player:
                return Response(code=codes.ALREADY_EXISTS, body="You already answered")
        
        if isinstance(request.body, dict):
            answer_obj = request.body.get("answer")

            if answer_obj:
                # Add new answer in actual question
                self.last_question.answers.append(Answer(player, answer_obj, answer_obj == self.last_question.correct_code))

                if answer_obj == self.last_question.correct_code:
                    self.round_hit = True
                
                return Response(code=codes.SUCCESS, body="OK")
        
        # Return invalid parameters
        return Response(code=codes.INVALID_PARAMETERS, body="Invalid params")


if __name__ == "__main__":
    questions = []
    for obj in load_json():
        obj["alternatives"] = [Alternative(**a) for a in obj["alternatives"]]
        questions.append(Question(**obj))

    try:
        server = ServerUDP(('localhost', 8081,))

        room = Room(socket=server.server_socket,questions=questions)

        server.router.add("/register", room.register, "ADD")
        server.router.add("/answer", room.answer, "ADD")

        server.start()
        room.start()
    
        while room.running:
            pass
    except:
        room.running = False
        
server.stop()