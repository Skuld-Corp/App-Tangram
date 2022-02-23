import os, sys
sys.path.append(os.path.normpath(os.getcwd() + os.sep + os.pardir))
from main import cria_app
import pytest


@pytest.fixture(scope="module")
def app():
    return cria_app()
