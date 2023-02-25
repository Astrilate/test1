from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from app import config


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.from_object(config)
db = SQLAlchemy(app)

