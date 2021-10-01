import json
import os

def load_setting():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    # with open('setting.json', 'r') as file:
    with open(os.path.join(__location__, 'setting.json'), 'r') as file:
        return json.load(file)[os.getenv('FLASK_ENV')]
