from .base import db, ma, bcrypt



class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, unique=True, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')


    def __init__(self, first_name, last_name,email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "phone_number", "email_confirmed")
        sqla_session = db.session


class UserRole(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer(),  db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'), default=1)






