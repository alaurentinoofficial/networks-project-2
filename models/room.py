from models.player import Player
from models.response import Response
from models.request import Request
from constants import codes

from typing import List

class Alternative():
    code: str
    text: str

    def __init__(self, code: str = None, text: str = None):
        self.code = code
        self.text = text
    
class Answer():
    id_player: str
    answer: str

    def __init__(self, id_player: str = None, answer: str = None):
        self.answer = answer
        self.alternative = id_player  

class Question():
    text: str
    correct_code: str
    alternatives: List[Alternative]
    answers: List[Answer]
    answered_players = List[Player]

    def __init__(self, text: str = None, correct_code: str = None, alternatives: List[Alternative] = []):
        self.text = text
        self.correct_code = correct_code
        self.alternatives = alternatives
        self.answers = []
        self.answered_players = []
    
    def reset(self):
        self.answers = []

class Room():
    game_state: int
    players: List[Player]
    questions: List[Question]
    answers: List[Answer]
    max_players: int

    def __init__(self, questions, players: List[Player] = [], answers: List[Answer] = [], max_players=5):
        self.questions = questions
        self.players = players
        self.answers = answers
        self.max_players = max_players