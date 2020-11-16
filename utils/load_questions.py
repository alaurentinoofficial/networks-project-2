import json
import random

def load_json(filename="questions.json", encoding="utf-8"):
    config = {}
    with open(filename, encoding=encoding) as file:
        config = json.load(file)
    
    return config

def random_sort(list_obj):
    list_obj = list_obj[:]
    random.shuffle(list_obj)

    return list_obj
