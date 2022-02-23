from scr import cria_app
from dotenv import load_dotenv
load_dotenv()

app = cria_app()

if __name__ == "__main__":
    app.run()
