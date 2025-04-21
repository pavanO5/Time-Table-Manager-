import os

class Config:
    SECRET_KEY = '05cc0ed9020aa0c8c0c84b34d5eabea2'  # For form security
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
