from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import wtforms_json
from flask_cors import CORS




wtforms_json.init()
app = Flask(__name__)
CORS(app)

# this will get configurations from config.py
app.config.from_object('config')

db = SQLAlchemy(app)


from app import views
