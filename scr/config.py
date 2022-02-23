import os

uri = os.getenv("DATABASE_URL")
# necessário pro Heroku
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

secreto = os.getenv("secret_key")

SECRET_KEY = secreto
SQLALCHEMY_DATABASE_URI = uri
SQALCHEMY_TRACK_MODIFICATIONS = False
if os.getenv("env") == "prod":
    DEBUG = False
else:
    DEBUG = True
    TESTING = True
