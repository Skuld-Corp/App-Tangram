from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate


db = SQLAlchemy()



def cria_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    migrate = Migrate(app, db)

    with app.app_context():
        db.init_app(app)
        login_manager = LoginManager()
        login_manager.login_view = 'views.login'
        login_manager.init_app(app)

        from .views import views
        from .auth import auth
        from .models import Usuario

        db.create_all()

        configura_roles(db=db)

        app.register_blueprint(views, url_prefix='/')
        app.register_blueprint(auth, url_prefix='/')

        @login_manager.user_loader
        def load_user(id):
            return Usuario.query.get(int(id))

        return app


def configura_roles(db):
    from .models import Roles
    verifica_tabela_cheia = Roles.query.filter_by(id=1).first()
    if not verifica_tabela_cheia:
        admin = Roles(nome="Admin", descricao="Permitir cadastrar professor")
        professor = Roles(nome="Professor", descricao="Permitir criar perguntas para os estudantes")
        estudante = Roles(nome="Estudante", descricao="Permitir respoder as perguntas e ter Tangramcoin")
        db.session.add(admin)
        db.session.add(professor)
        db.session.add(estudante)
        db.session.commit()

