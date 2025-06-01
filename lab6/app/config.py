import os

SECRET_KEY = 'secret-key'

# SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin:admin142&hs@91.132.58.61:3306/lab6'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    '..',
    'media', 
    'images'
)
