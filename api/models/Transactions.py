from .base import db, ma


class Transaction(db.Model):
    __tablename__ = "transactions"

    DEPOSIT = 'DP'
    WITHDRAWAL = 'WD'

    CREDIT = 'CD'
    DEBIT = 'DB'

    APPROVED = 'AP'
    FAILED = 'FA'
    PENDING = 'PD'

    ADMIN = 'AD'

    TRANSACTION_STATES = (
        (APPROVED, 'approved'),
        (PENDING, 'pending'),
        (FAILED, 'failed')
    )

    TRANSACTION_TYPES = (
        (CREDIT, 'credit'),
        (DEBIT, 'debit')
    )

    TRANSACTION_MODES = (
        (DEPOSIT, 'deposit'),
        (WITHDRAWAL, 'withdrawal')
    )

    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String)
    to_currency = db.Column(db.String)
    amount = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    wallet_id = db.Column(db.String)
    status = db.Column(db.String)
    mode = db.Column(db.String)
    type = db.Column(db.String)


class TransactionSchema(ma.Schema):
    class Meta:
        model = Transaction
        fields = (
        'id', 'wallet_id', 'status', 'amount', 'type', 'mode', 'user_id')


transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)

