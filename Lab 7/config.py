import os
basedir = os.path.abspath(os.path.dirname(__file__))

# General Config
WTF_CSRF_ENABLED = True
SECRET_KEY = 'safdfsdgf'

# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'site.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
