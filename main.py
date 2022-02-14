from scr import cria_app

env = "prod"

app = cria_app(env)

if __name__ == "__main__":
    app.run()
