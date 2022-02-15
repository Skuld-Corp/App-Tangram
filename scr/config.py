import os
import re

uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

secreto = os.getenv("secret_key")

SECRET_KEY = secreto
SQLALCHEMY_DATABASE_URI = uri
SQALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = False
