from flask import Flask

app = Flask(__name__)

# Import the routes after initializing the app
from .routes import *

def create_app():
    return app
