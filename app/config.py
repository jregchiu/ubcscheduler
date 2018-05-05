import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://jchiu:@/schedulerdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
