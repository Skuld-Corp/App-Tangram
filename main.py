from scr import cria_app

env = "dev"

app = cria_app(env)

if __name__ == "__main__":
    app.run()
