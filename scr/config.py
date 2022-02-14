import os
import re

uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


SECRET_KEY = "secreto"
SQLALCHEMY_DATABASE_URI = uri
SQALCHEMY_TRACK_MODIFICATIONS = False
