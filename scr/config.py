import os
import re

uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


SECRET_KEY = "adas@asdsad%ads*das#da5478"
SQLALCHEMY_DATABASE_URI = uri
SQALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = False
