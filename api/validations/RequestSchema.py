from marshmallow import fields, Schema, validate, ValidationError, validates_schema


class Register(Schema):
    first_name = fields.String(required=True,
                               error_messages={"required": "First name is required.",
                                               "min": "First name must be greater than 2 characters.",
                                               "max": "First name must be less than 15 characters."},
                               validate=validate.Length(min=3, max=15)
                               )

    last_name = fields.String(required=True,
                              error_messages={"required": "Last name is required."},
                              validate=validate.Length(min=3, max=15)
                              )

    email = fields.Email(required=True)

    password = fields.String(required=True,
                             error_messages={"required": "Password is required",
                                             "min": "Password must be greater than 4 characters.",
                                             "max": "Password must be within 4 - 50 characters."},
                             validate=validate.Length(min=4, max=50)
                             )

    account_type = fields.String(required=True)
    main_currency = fields.String(required=False)

    @validates_schema
    def validate_main_currency(self, data, **kwargs):

        # If user is admin then...no need for a main_currency field
        try:
            if data['account_type'].lower() == 'admin' and data['main_currency']:
                raise ValidationError("An admin can`t have a wallet, please discard the main_currency field")

        # If a key error is thrown, then the field is not there, we approve.
        except KeyError:
            return True

        # If user is not an admin, we require a main_currency field
        if data['account_type'].lower() != 'admin':
            try:
                main_currency = data['main_currency']
            except KeyError:
                raise ValidationError('please submit a main_currency field')

        main_currency = data['main_currency'].upper()
        supported_currencies = ['USD', 'AUD', 'CAD', 'PLN', 'NGN']
        if main_currency not in supported_currencies:
            raise ValidationError("Sorry, we don`t support the submitted currency. please choose between 'USD','AUD',"
                                  "'CAD','PLN','NGN'")
        return True

    @validates_schema
    def validate_account_type(self, data, **kwargs):
        account_type = data['account_type'].lower()
        supported_types = ['elite', 'noob', 'admin']
        if account_type not in supported_types:
            raise ValidationError("Please submit a valid account type. Choose either Noob or Elite")
        return True


class Login(Schema):
    email = fields.Email(required=True, error_messages={"required": "Please enter a valid email address."})
    password = fields.String(required=True, error_messages={"required": "Password is required"})


class FundSchema(Schema):
    amount = fields.String(required=True)
    purchase_currency = fields.String()

    @validates_schema
    def validate_main_currency(self, data, **kwargs):


        purchase_currency = data['purchase_currency'].upper()
        supported_currencies = ['USD', 'AUD', 'CAD', 'PLN', 'NGN']
        if purchase_currency not in supported_currencies:
            raise ValidationError("Sorry, we don`t support the submitted currency. please choose between 'USD','AUD',"
                                  "'CAD','PLN','NGN'")
        return True


class WithdrawSchema(Schema):
    withdrawal_amount = fields.String(required=True)
    withdrawal_currency = fields.String(required=True)

    @validates_schema
    def validate_main_currency(self, data, **kwargs):
        withdrawal_currency = data['withdrawal_currency'].upper()
        supported_currencies = ['USD', 'AUD', 'CAD', 'PLN', 'NGN']
        if withdrawal_currency not in supported_currencies:
            raise ValidationError("Sorry, we don`t support the submitted currency. please choose between 'USD','AUD',"
                                  "'CAD','PLN','NGN'")
        return True


class AdminApproveSchema(Schema):
    transaction_id = fields.String(required=True)



class AdminFundsUser(Schema):
    user_id = fields.String(required=True)
    amount = fields.String(required=True)
    currency = fields.String()

    @validates_schema
    def validate_main_currency(self, data, **kwargs):


        currency = data['currency'].upper()
        supported_currencies = ['USD', 'AUD', 'CAD', 'PLN', 'NGN']
        if currency not in supported_currencies:
            raise ValidationError("Sorry, we don`t support the submitted currency. please choose between 'USD','AUD',"
                                  "'CAD','PLN','NGN'")
        return True


class AdminChangeUserCurrency(Schema):
    user_id = fields.String(required=True)
    currency = fields.String(required=True)

    @validates_schema
    def validate_main_currency(self, data, **kwargs):
        currency = data['currency'].upper()
        supported_currencies = ['USD', 'AUD', 'CAD', 'PLN', 'NGN']
        if currency not in supported_currencies:
            raise ValidationError("Sorry, we don`t support the submitted currency. please choose between 'USD','AUD',"
                                  "'CAD','PLN','NGN'")
        return True



class AdminPromoteUser(Schema):
    user_id = fields.String(required=True)
    role = fields.String(required=True)

    @validates_schema
    def validate_account_type(self, data, **kwargs):
        account_type = data['role'].lower()
        supported_types = ['elite', 'noob', 'admin']
        if account_type not in supported_types:
            raise ValidationError("Please submit a valid account type. Choose either Noob, Elite or Admin")
        return True


class BalanceSchema(Schema):
    wallet_id = fields.String(required=True)