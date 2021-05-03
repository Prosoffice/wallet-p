import decimal

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from api.core import create_response, create_validation_err_response
from api.models import User, UserRole, Wallet, db
from api.models import Role
from api.models.Transactions import Transaction, transactions_schema
from api.tools.utils import convert_curr
from api.validations.RequestSchema import AdminFundsUser, AdminChangeUserCurrency, AdminPromoteUser

admin = Blueprint('admin', __name__)


# RUN THIS CODE BEFORE ANY ADMIN REQUEST IS ATTENDED TO, ENSURE USER IS ADMIN
@admin.before_request
@jwt_required()
def before_request():
    current_user = get_jwt_identity()
    user_role = UserRole.query.filter_by(user_id=current_user['id']).first()
    role = Role.query.filter_by(id=user_role.role_id).first()
    if not (role.role_title == 'admin'):
        return create_response(success=0, message='Restricted area.', status=403)


@admin.route('/pending-deposits', methods=['GET'])
@jwt_required()
def pending_deposits():
    all_pending = Transaction.query.filter_by(status=Transaction.PENDING, mode=Transaction.DEPOSIT).all()
    data = transactions_schema.dump(all_pending)
    return create_response(data=data, success=1, status=200)


@admin.route('/pending-withdrawals', methods=['GET'])
@jwt_required()
def pending_withdrawals():
    all_pending = Transaction.query.filter_by(status=Transaction.PENDING, mode=Transaction.WITHDRAWAL).all()
    data = transactions_schema.dump(all_pending)
    return create_response(data=data, success=1, status=200)


@admin.route('/approve-fund/<int:id>', methods=['GET'])
@jwt_required()
def approve_deposit(id):
    transaction = Transaction.query.filter_by(id=id, mode=Transaction.DEPOSIT).first()
    if not transaction:
        return create_response(success=0, message='Invalid transaction id', status=400)

    if transaction.status != transaction.PENDING:
        return create_response(success=0, message='Transaction already approved/Declined', status=400)

    wallet_id = transaction.wallet_id
    wallet_obj = Wallet.query.filter_by(wallet_id=wallet_id).first()
    wallet_obj.balance += decimal.Decimal(transaction.amount)
    db.session.add(wallet_obj)
    db.session.commit()

    transaction.status = Transaction.APPROVED
    db.session.add(transaction)
    db.session.commit()

    return create_response(data=None, success=1, status=200, message="Transaction Approved!")


@admin.route('/approve-withdrawal/<int:id>', methods=['GET'])
@jwt_required()
def approve_withdrawal(id):
    transaction = Transaction.query.filter_by(id=id, mode=Transaction.WITHDRAWAL).first()
    if not transaction:
        return create_response(success=0, message='Invalid transaction id', status=400)

    if transaction.status != transaction.PENDING:
        return create_response(success=0, message='Transaction already approved/Declined', status=400)

    wallet_id = transaction.wallet_id
    wallet_obj = Wallet.query.filter_by(wallet_id=wallet_id).first()
    wallet_obj.balance -= decimal.Decimal(transaction.amount)
    db.session.add(wallet_obj)
    db.session.commit()

    transaction.status = Transaction.APPROVED
    db.session.add(transaction)
    db.session.commit()

    return create_response(data=None, success=1, status=200, message="Transaction Approved!")



@admin.route('/change_main_currency', methods=['POST'])
@jwt_required()
def change_currency():
    try:
        body = request.get_json()
        result = AdminChangeUserCurrency().load(body)

        currency = body['currency'].lower()
        user_id = body['user_id']

        present = Wallet.query.filter_by(id=user_id, is_main=1).first()
        print(present.wallet_id)
        if present.currency == currency:
            return create_response(success=0, message=f"Wallet already in {currency.upper()}", status=400)

        # convert balance to new currency
        balance = present.balance
        if balance != 0:
            converted_amount, status = convert_curr(present.currency, currency, balance)
            if status:
                balance = converted_amount
            else:
                return create_response(success=0, message=f"Conversion error, please try again", status=400)

        present.currency = currency
        present.balance = balance
        db.session.add(present)
        db.session.commit()

        data= {
            'wallet_id': present.wallet_id,
            'main_currency': currency.upper()
        }
        return create_response(data=data, success=1, status=200, message="Success! currency changed.")
    except ValidationError as err:
        return create_validation_err_response(data=err.messages, status=400, success=0)


@admin.route('/fund_user', methods=['POST'])
@jwt_required()
def fund_user():
    user = User.query.filter_by(id=(get_jwt_identity())['id']).first()
    try:
        body = request.get_json()
        result = AdminFundsUser().load(body)

        fund_amount = body['amount']
        purchase_currency = body['currency'].lower()
        customer = body['user_id']


        customer = User.query.filter_by(id=customer).first()
        if not customer:
            return create_response(success=0, message=f"User id {customer} does not exist", status=400)


        # What role is the customer?
        user_role_key = UserRole.query.filter_by(user_id=customer.id).first()
        user_role = Role.query.filter_by(id=user_role_key.role_id).first()

        if user_role.role_title == 'noob':

            # Validate/Retrieve user wallet from db
            user_wallet = Wallet.query.filter_by(user_id=customer.id, is_main=1).first()

            if purchase_currency == user_wallet.currency:
                pass

            else:
                converted_amount, status = convert_curr(purchase_currency, user_wallet.currency, fund_amount)
                if status:
                    fund_amount = converted_amount
                    print(fund_amount)
                else:
                    return create_response(success=0, message="An Error occurred. please try again", status=200)

            new_tx = Transaction()
            new_tx.amount = fund_amount
            new_tx.from_currency = purchase_currency
            new_tx.to_currency = user_wallet.currency
            new_tx.status = Transaction.PENDING
            new_tx.mode = Transaction.DEPOSIT
            new_tx.type = Transaction.CREDIT
            new_tx.wallet_id = user_wallet.wallet_id
            new_tx.user_id = customer.id

            db.session.add(new_tx)
            db.session.commit()

            data = {
                "wallet_id": user_wallet.wallet_id,
                "currency": user_wallet.currency.upper(),
                "fund_amount": str(fund_amount)
            }

            return create_response(data=data, success=1, status=200, message="Funds successfully received, Awaiting "
                                                                             "approval")
        elif user_role.role_title == 'elite':

            # Retrieve/create wallet
            user_wallet = Wallet.query.filter_by(user_id=customer.id, currency=purchase_currency).first()
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
                "currency": purchase_currency.upper(),
                "fund_amount": str(fund_amount)
            }
            return create_response(data=data, success=1, status=200, message="CREDIT! Funds successfully received.")


    except ValidationError as err:
        return create_validation_err_response(data=err.messages, status=400, success=0)



@admin.route('/change-user-role', methods=['POST'])
@jwt_required()
def promote_or_demote_user():
    try:
        body = request.get_json()
        result = AdminPromoteUser().load(body)

        role = body['role'].lower()
        user_id = body['user_id']

        present = User.query.filter_by(id=user_id).first()
        if not present:
            return create_response(success=0, message=f"No user with user_id{user_id}", status=400)

        # Get the role id from the role model
        role_obj = Role.query.filter_by(role_title=role).first()
        role_id = role_obj.id

        # Update user`s role in the User_role model
        user_role_obj = UserRole.query.filter_by(user_id=user_id).first()

        user_role_obj.role_id = role_id
        db.session.add(user_role_obj)
        db.session.commit()

        data = {
            'user_id': user_id,
            'role': role.upper()
        }

        return create_response(data=data, success=1, status=200,
                               message=f"Success! User role changed to {role.upper()}.")
    except ValidationError as err:
        return create_validation_err_response(data=err.messages, status=400, success=0)