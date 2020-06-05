from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import wtforms_json


wtforms_json.init()
app = Flask(__name__)

# this will get configurations from config.py
app.config.from_object('config')

db = SQLAlchemy(app)


from app import views
