from scr import cria_app
import os
from dotenv import load_dotenv
load_dotenv()

env = os.getenv("env")

app = cria_app(env)

if __name__ == "__main__":
    app.run()
