from app import db
from .base_model import BaseModel

class User(BaseModel):
    id = db.Column(db.Integer,primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(100),index=True,unique=True, nullable=False)
    password = db.Column(db.String(140), nullable=False)
    event = db.relationship('Event', backref='user', lazy='dynamic')
    admin = db.Column(db.Boolean,default=0,nullable=False)
    
    # fields that are always returned by to_dict method
    _default_fields = [
        'id',
        'email'
    ]

    # fields that are never returned by to_dict method
    _hidden_fields = [
        'password'
    ]

    # fields that are never updated by from_dict method
    _readonly_fields = [
        'id'
    ]

    def __repr__(self):
        return "<User %r>" % (self.email)


class Event(BaseModel):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    description = db.Column(db.String(150),nullable=False)
    category = db.Column(db.String(100),nullable=False)
    start_date = db.Column(db.DateTime,nullable=False)
    end_date = db.Column(db.DateTime,nullable=False)
    cost = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False, default=0)
    venue = db.Column(db.String(100))
    flyer = db.Column(db.String(100))
    visbility = db.Column(db.Boolean,default=0, nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    # fields that are always returned by to_dict method
    _default_fields = [
        'id',
        'name',
        'category'
    ]

    # fields that are never returned by to_dict method
    _hidden_fields = []

    # fields that are never updated by from_dict method
    _readonly_fields = [
        'id',
        'user_id'
    ]

    