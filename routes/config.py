import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Config:
    SQLALCHEMY_DATABASE_URI = (
        'mysql+mysqlconnector://lms_user:password@localhost:3306/lms_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'learn-by-tech'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
