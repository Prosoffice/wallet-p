import decimal

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from api.core import create_validation_err_response, create_response
from api.models import User, Wallet, UserRole, Role, db
from api.models.Transactions import Transaction
from api.tools.utils import convert_curr
from api.validations.RequestSchema import FundSchema, WithdrawSchema, BalanceSchema

transactions = Blueprint('transactions', __name__)


# RUN THIS CODE BEFORE ANY ADMIN REQUEST IS ATTENDED TO, ENSURE USER IS NOT ADMIN
@transactions.before_request
@jwt_required()
def before_request():
    current_user = get_jwt_identity()
    user_role = UserRole.query.filter_by(user_id=current_user['id']).first()
    role = Role.query.filter_by(id=user_role.role_id).first()
    if role.role_title == 'admin':
        return create_response(success=0, message='Restricted area, you are an admin', status=403)


@transactions.route('/fund', methods=['POST'])
@jwt_required()
def fund_wallet():
    user = User.query.filter_by(id=(get_jwt_identity())['id']).first()
    try:
        body = request.get_json()
        result = FundSchema().load(body)

        fund_amount = body['amount']
        purchase_currency = body['purchase_currency'].lower()

        # What role is the user?
        user_role_key = UserRole.query.filter_by(user_id=user.id).first()
        user_role = Role.query.filter_by(id=user_role_key.role_id).first()

        if user_role.role_title == 'noob':

            # Validate/Retrieve user wallet from db
            user_wallet = Wallet.query.filter_by(user_id=user.id, is_main=1).first()

            if purchase_currency == user_wallet.currency:
                pass

            else:
                converted_amount, status = convert_curr(purchase_currency, user_wallet.currency, fund_amount)
                if status:
                    fund_amount = converted_amount
                else:
                    return create_response(success=0, message="An Error occurred. please try again", status=400)


            new_tx = Transaction()
            new_tx.amount = fund_amount
            new_tx.from_currency = purchase_currency
            new_tx.to_currency = user_wallet.currency
            new_tx.status = Transaction.PENDING
            new_tx.mode = Transaction.DEPOSIT
            new_tx.type = Transaction.CREDIT
            new_tx.wallet_id = user_wallet.wallet_id
            new_tx.user_id = user.id

            db.session.add(new_tx)
            db.session.commit()

            data = {
                "wallet_id": user_wallet.wallet_id,
                "currency": user_wallet.currency,
                "fund_amount": str(fund_amount)
            }

            return create_response(data=data, success=1, status=200, message="Funds successfully received, Awaiting "
                                                                             "approval") 
        elif user_role.role_title == 'elite':

            # Retrieve/create wallet
            user_wallet = Wallet.query.filter_by(user_id=user.id, currency=purchase_currency).first()
            if not user_wallet:
                print("Wallet not found, creating wallet....")
                new_wallet = Wallet(user_id=user.id, currency=purchase_currency, is_main=0)
                db.session.add(new_wallet)
                db.session.commit()

                # Set user wallet to new wallet
                user_wallet = new_wallet

            user_wallet.balance += decimal.Decimal(fund_amount)
            db.session.add(user_wallet)
            db.session.commit()

            # register a new transaction

            new_tx = Transaction()
            new_tx.amount = fund_amount
            new_tx.from_currency = purchase_currency
            new_tx.to_currency = user_wallet.currency
            new_tx.status = Transaction.APPROVED
            new_tx.mode = Transaction.DEPOSIT
            new_tx.type = Transaction.CREDIT
            new_tx.wallet_id = user_wallet.wallet_id
            new_tx.user_id = user.id

            db.session.add(new_tx)
            db.session.commit()

            data = {
                "wallet_id": user_wallet.wallet_id,
                "currency": purchase_currency,
                "fund_amount": str(fund_amount)
            }
            return create_response(data=data, success=1, status=200, message="CREDIT! Funds successfully received.")

    except ValidationError as err:
        return create_validation_err_response(data=err.messages, status=400, success=0)


@transactions.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    user = User.query.filter_by(id=(get_jwt_identity())['id']).first()

    try:
        body = request.get_json()
        result = WithdrawSchema().load(body)

        withdraw_amount = body['withdrawal_amount']
        withdraw_currency = body['withdrawal_currency'].lower()

        # What role is the user?
        user_role_key = UserRole.query.filter_by(user_id=user.id).first()
        user_role = Role.query.filter_by(id=user_role_key.role_id).first()


        if user_role.role_title == 'noob':
            # Retrieve user wallet from db
            user_wallet = Wallet.query.filter_by(user_id=user.id, is_main=1).first()

            if withdraw_currency == user_wallet.currency:
                if user_wallet.balance >= decimal.Decimal(withdraw_amount):
                    pass
                else:
                    return create_response(success=0, message="Insufficient funds", status=400)
            else:
                converted_amount, status = convert_curr(withdraw_currency, user_wallet.currency, withdraw_amount)
                if status:
                    if user_wallet.balance >= converted_amount:
                        withdraw_amount = converted_amount
                    else:
                        return create_response(success=0, message="Insufficient funds", status=400)
                else:
                    return create_response(success=0, message="An Error occurred. please try again", status=400)

            db.session.add(user_wallet)
            db.session.commit()

            new_tx = Transaction()
            new_tx.amount = withdraw_amount
            new_tx.from_currency = withdraw_currency
            new_tx.to_currency = user_wallet.currency
            new_tx.status = Transaction.PENDING
            new_tx.mode = Transaction.WITHDRAWAL
            new_tx.type = Transaction.DEBIT
            new_tx.wallet_id = user_wallet.wallet_id
            new_tx.user_id = user.id

            db.session.add(new_tx)
            db.session.commit()

            data = {
                "wallet_id": user_wallet.wallet_id,
                "withdrawal_amount": str(withdraw_amount),
                "withdrawal_currency": withdraw_currency
            }

            return create_response(data=data, success=1, status=200, message="Funds withdrawal request sent, Awaiting "
                                                                             "approval")
        elif user_role.role_title == 'elite':

            # Retrieve/create wallet

            user_wallet = Wallet.query.filter_by(user_id=user.id, currency=withdraw_currency).first()
            if user_wallet and user_wallet.balance >= decimal.Decimal(withdraw_amount):
                user_wallet.balance -= decimal.Decimal(withdraw_amount)
                db.session.add(user_wallet)
                db.session.commit()

                # Establish new transaction
                new_tx = Transaction()
                new_tx.amount = withdraw_amount
                new_tx.from_currency = withdraw_currency
                new_tx.to_currency = user_wallet.currency
                new_tx.status = Transaction.APPROVED
                new_tx.mode = Transaction.WITHDRAWAL
                new_tx.type = Transaction.DEBIT
                new_tx.wallet_id = user_wallet.wallet_id
                new_tx.user_id = user.id

                db.session.add(new_tx)
                db.session.commit()
            elif not user_wallet or user_wallet.balance <= decimal.Decimal(withdraw_amount):

                # Fetch main wallet immediately!
                main_wallet = Wallet.query.filter_by(user_id=user.id, is_main=1).first()

                # Retrieve the currency equivalent

                converted_amount, status = convert_curr(withdraw_currency, main_wallet.currency, withdraw_amount)
                if status:
                    if main_wallet.balance >= converted_amount:
                        main_wallet.balance -= converted_amount
                        withdraw_amount = converted_amount

                        db.session.add(main_wallet)
                        db.session.commit()

                        # Establish new transaction
                        new_tx = Transaction()
                        new_tx.amount = converted_amount
                        new_tx.from_currency = withdraw_currency
                        new_tx.to_currency = main_wallet.currency
                        new_tx.status = Transaction.APPROVED
                        new_tx.mode = Transaction.WITHDRAWAL
                        new_tx.type = Transaction.DEBIT
                        new_tx.wallet_id = main_wallet.wallet_id
                        new_tx.user_id = user.id

                        db.session.add(new_tx)
                        db.session.commit()
                    else:
                        return create_response(success=0, message="Insufficient funds", status=400)
                else:
                    return create_response(success=0, message="An Error occurred. please try again", status=400)
            else:
                return create_response(success=0, message="Insufficient funds", status=400)

            if not user_wallet:
                user_wallet = None
            else:
                user_wallet = user_wallet.wallet_id

            data = {
                "wallet_id": user_wallet,
                "withdrawal_amount": str(withdraw_amount),
                "withdrawal_currency": withdraw_currency
            }
            return create_response(data=data, success=1, status=200, message="DEBIT! Funds successfully disbursed.")


    except ValidationError as err:
        return create_validation_err_response(data=err.messages, status=400, success=0)


@transactions.route('/get-balance', methods=['POST'])
@jwt_required()
def get_balance():
    user = User.query.filter_by(id=(get_jwt_identity())['id']).first()

    try:
        body = request.get_json()
        result = BalanceSchema().load(body)

        wallet_id = body['wallet_id']

        wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=user.id).first()
        if not wallet:
            return create_response(success=0, message=f"Wallet id {wallet_id} does not exist or doesn`t belong to you", status=400)

        balance = wallet.balance

        data = {
            'balance': str(balance),
            'currency': wallet.currency
        }
        return create_response(data=data, success=1, status=200, message="")

    except ValidationError as err:
        return create_validation_err_response(data=err.messages, status=400, success=0)