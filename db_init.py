from app import db
from app.models import User, Event
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash as pw


"""
Run this file to clear your old db tables and initialize new ones with the properties below
"""
db.drop_all()
db.create_all()

# Templates
# u1 = User(firstname="", lastname="", email="", password="", admin=False)

# e1 = Event(title="", description="", category="", start_date=datetime(2020,2,20,8), 
#            end_date=datetime(2020,2,20,8) + timedelta(hours=3), cost=5000, visibility=False, user_id=1)


def pwrd(password):
    return pw(password, method="sha256")

u1 = User(firstname="John", lastname="Wick", email="jwick@thecontinental.com", password=pwrd("gunner"), admin=True)
u2 = User(firstname="Harry", lastname="Potter", email="h.potter@hogwarts.com", password=pwrd("wizard"), admin=False)
u3 = User(firstname="Nathaniel", lastname="Christie", email="nc_hammer@gmail.com", password=pwrd("cant touch"), admin=False)
u4 = User(firstname="Kayla", lastname="Effs", email="keffs@gmail.com", password=pwrd("kyeeks"), admin=False)

e1 = Event(title="Continental Breakfast", description="Assasins' breakfast retreat", category="Dining", start_date=datetime(2020,2,20,8), 
           end_date=datetime(2020,2,20,8) + timedelta(hours=2), cost=5000, visibility=False, user_id=1)
e2 = Event(title="Yule Ball", description="In celebration of the Triwizard Tournament", category="Party", start_date=datetime(2020,3,15,19), 
           end_date=datetime(2020,3,15,19) + timedelta(hours=5), cost=46000, visibility=False, user_id=2)
e3 = Event(title="NCB Presentation", description="Sprint 8 Server Side Essentials Demo", category="Conference", start_date=datetime(2020,6,11,14), 
           end_date=datetime(2020,6,11,14) + timedelta(hours=3), cost=46000, visibility=True, user_id=3)
e4 = Event(title="Dog Tamer's Conference", description="Learn how to keep your dog alive", category="Conference", start_date=datetime(2020,6,11,8), 
           end_date=datetime(2020,6,11,8) + timedelta(hours=5), cost=900000, visibility=True, user_id=1)

db.session.add(u1)
db.session.add(u2)
db.session.add(u3)
db.session.add(u4)
db.session.add(e1)
db.session.add(e2)
db.session.add(e3)
db.session.add(e4)
db.session.commit()

if __name__ == "__main__":
    pass
    # db.session.add(u1)
    # db.session.add(u2)
    # db.session.add(u3)
    # db.session.add(u4)
    # db.session.add(e1)
    # db.session.add(e2)
    # db.session.add(e3)
    # db.session.add(e4)
    # db.session.commit()
