import os
import pytest
from api import create_app
from api.models import db, Role, User


@pytest.fixture
def app():
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'postgresql://nxddzhrhitjuox:4f3a0a4536df67e1352d7b062ff348ab0fa92c2ac994e0445ab1828019bcb86b@ec2-54-166-167-192.compute-1.amazonaws.com:5432/ddradrs416avtu',
        'DEBUG': True,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    with app.app_context():
        db.create_all()
        noob = Role('noob')
        elite = Role('elite')
        admin = Role('admin')
        db.session.add(noob)
        db.session.add(elite)
        db.session.add(admin)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


"""DUMMY DATA COLLECTION"""
DUMMY_REG = {
    "first_name": "Juber",
    "last_name": "Ogbonnaya",
    "email": "henryjuber@gmail.com",
    "password": "chinonyerem",
    "account_type": "elite", # Can be changed to Elite of Admin to redefine the client
    "main_currency": "ngn"
}

DUMMY_LOGIN = {
    "email": "henryjuber@gmail.com",
    "password": "chinonyerem"
}

DUMMY_FUND = {
    "amount": "5000",
    "purchase_currency": "ngn"
}

DUMMY_WITHDRAW = {
    "withdrawal_amount": "0",
    "withdrawal_currency": "usd"
}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


"""TEST INDEX"""


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    print(f"{bcolors.OKGREEN}Index test PASSED!")


"""TEST REGISTER"""


def test_register(client, app):
    # test for successful response
    response = client.post('/register', json=DUMMY_REG)
    assert response.status_code == 201

    # test that the user was inserted into the database
    with app.app_context():
        user = User.query.filter_by(email=DUMMY_REG['email']).first()
        assert (user)
    assert b'Registration successful. Please login to receive auth token' in response.data
    print(f"{bcolors.OKGREEN}Registration test PASSED!")


"""TEST LOGIN"""


def test_login(client, app):
    # Register user
    client.post('/register', json=DUMMY_REG)

    # Login user
    response = client.post('/login', json=DUMMY_LOGIN)
    assert response.status_code == 200
    assert b'Login successful!' in response.data
    print(f"{bcolors.OKGREEN}Login test PASSED!")


def authenticate(user, app):
    user.post('/register', json=DUMMY_REG)
    response = user.post('/login', json=DUMMY_LOGIN)
    token = response.get_json()['token']
    return token


"""TEST FUND WALLET"""


def test_fund_wallet(client, app):
    token = authenticate(client, app)
    response = client.post('/transactions/fund', json=DUMMY_FUND, headers={
        'Authorization': 'Bearer {}'.format(token)
    }, content_type='application/json')
    assert response.status_code == 200
    print(f"{bcolors.OKGREEN}FUND test PASSED!")


"""TEST WITHDRAW WALLET"""


def test_withdraw_wallet(client, app):
    token = authenticate(client, app)
    response = client.post('/transactions/withdraw', json=DUMMY_WITHDRAW, headers={
        'Authorization': 'Bearer {}'.format(token)
    }, content_type='application/json')
    assert response.status_code == 200
    print(f"{bcolors.OKGREEN}WITHDRAW test PASSED!")
