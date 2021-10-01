import toml
import os

def load_setting():
    return toml.load('env.toml')[os.getenv('FLASK_ENV')]

