from flask import Blueprint, request

from api.models import db, Role, User, UserSchema, UserRole, bcrypt, Role, Wallet
from api.core import create_response, create_validation_err_response
from api.validations.RequestSchema import Register, Login
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
import datetime
import base64

from ..message import message
import random

main = Blueprint("main", __name__)  # initialize blueprint


# function that is called when you visit /
@main.route("/", methods=["GET"])
def index():
    return create_response(message=message['HOME'], success=1, status=200)


@main.route("/info", methods=["GET"])
@jwt_required()
def info():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['id']).first()
    is_admin = user.is_admin
    verified = user.is_account_confirmed
    return create_response(data=UserSchema().dump(user), success=1, status=200)


@main.route("/login", methods=["POST"])
def login():
    try:
        body = request.get_json()
        result = Login().load(body)

        user = User.query.filter_by(email=request.json.get("email")).first()
        
        if user and bcrypt.check_password_hash(user.password, request.json.get("password")):
            expires = datetime.timedelta(days=7)
            access_token = create_access_token(identity={'id': user.id}, expires_delta=expires)
            
            try:
                dectken = access_token.decode('utf-8')
                return create_response(token=dectken, status=200, success=1, message="Login successful!")
            except:
                return create_response(token=access_token, status=200, success=1, message="Login successful!")
        else:
            return create_response(message=message['INCORRECT_LOGIN_CREDENTIALS'], success=0, status=400)
    except ValidationError as err:
        return create_validation_err_response(data=err.messages, status=400, success=0)


@main.route("/register", methods=["POST"])
def register():
    try:
        body = request.get_json()
        result = Register().load(body)

        email_exists = User.query.filter_by(email=body['email']).first()
        if email_exists:
            return create_response(success=0, message=message['EMAIL_EXISTS'], status=400)

        password_hash = bcrypt.generate_password_hash(
            body['password']).decode('utf-8')


        user = User(
            first_name=body['first_name'],
            last_name=body['last_name'],
            email=body['email'],
            password=password_hash,
        )
        db.session.add(user)
        db.session.commit()

        
        # ASSIGN USER TYPE UPON REGISTRATION
        role = Role.query.filter_by(role_title=body['account_type'].lower()).first()
        assigned_role = UserRole(user_id=user.id, role_id=role.id)
        db.session.add(assigned_role)
        db.session.commit()

        data = None
        # WALLET CONSTRUCT. MAIN CURRENCY DETERMINED UPON REGISTRATION
        if body['account_type'].lower() != 'admin':
            main_currency = body['main_currency']

            new_wallet = Wallet(user_id=user.id, is_main=1, currency=main_currency.lower())
            db.session.add(new_wallet)
            db.session.commit()
            
            wallet_id = new_wallet.wallet_id
            data = {
                "wallet_id":wallet_id
            }
        
        return create_response(data=data, success=1, message=message['REGISTRATION_SUCCESS'], status=201)

    except ValidationError as err:
        return create_validation_err_response(data=err.messages, status=400, success=0)





