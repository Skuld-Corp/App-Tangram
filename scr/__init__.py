from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
scheme = 'bancoskuld'
db_senha = 'Vv220621*'
db_user = 'root'


def cria_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "secreto"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_user}:{db_senha}@127.0.0.1:3306/{scheme}'
    app.config['SQALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.init_app(app)
        login_manager = LoginManager()
        login_manager.login_view = 'views.login'
        login_manager.init_app(app)

        from .views import views
        from .auth import auth
        from .models import Usuario

        db.create_all()

        app.register_blueprint(views, url_prefix='/')
        app.register_blueprint(auth, url_prefix='/')

        @login_manager.user_loader
        def load_user(id):
            return Usuario.query.get(int(id))

        return app





