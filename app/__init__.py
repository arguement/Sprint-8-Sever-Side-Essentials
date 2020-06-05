from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# this will get configurations from config.py
app.config.from_object('config')

db = SQLAlchemy(app)


from app import views
