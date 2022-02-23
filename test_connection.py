from flask import url_for
import pytest
from main import cria_app

@pytest.fixture(scope="module")
def app():
    return cria_app()


def test_app_criado_com_sucesso(app):
    assert app.name == 'scr'


def test_conectando_a_home_sem_login(client):
    assert client.get(url_for('views.home')).status_code == 302


def test_conectando_a_login(client):
    assert client.get(url_for('views.login')).status_code == 200


def test_conectando_a_cadastro(client):
    assert client.get(url_for('views.cadastro')).status_code == 200


def test_conectando_a_reset_de_senha(client):
    assert client.get(url_for('views.reset_senha')).status_code == 200

