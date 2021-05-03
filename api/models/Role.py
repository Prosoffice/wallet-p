from .base import db


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    role_title = db.Column(db.String)

    def __init__(self, title):
        self.role_title = title