from scr import cria_app
import os


env = os.getenv("env")

app = cria_app(env)

if __name__ == "__main__":
    app.run()
