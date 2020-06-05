from app import db

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(100),index=True,unique=True)
    password = db.Column(db.String(140))
    event = db.relationship('Event', backref='user')
    admin = db.Column(db.Boolean,default=0)
    

    def __repr__(self):
        return "<User %r>" % (self.email)


class Event(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    description = db.Column(db.String(100),nullable=False)
    category = db.Column(db.String(100),nullable=False)
    title = db.Column(db.String(100),nullable=False)
    start_date = db.Column(db.DateTime,nullable=False)
    end_date = db.Column(db.DateTime,nullable=False)
    cost = db.Column(db.String(100))
    venue = db.Column(db.String(100))
    flyer = db.Column(db.String(100))
    visbility = db.Column(db.Boolean,default=0)
    
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    