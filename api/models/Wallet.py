from .base import db
from ..tools.utils import generate_code, generate_wallet_id


class Wallet(db.Model):
    __tablename__ = "wallet"
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String)
    balance = db.Column(db.Numeric, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_main = db.Column(db.Integer, default=0)
    wallet_id = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, currency, user_id, is_main):
        self.currency = currency.lower(),
        self.user_id = user_id,
        self.is_main = is_main,
        wallet_id = generate_wallet_id()
        self.wallet_id = wallet_id

    def get_balance(self):
        return self.balance

    def __repr__(self):
        return '<Wallet id{}>'.format(self.wallet_id)

