import unittest
from flask_testing import TestCase
from app import app,db
from app.models import User,Event
import json




class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        app.config["DEBUG"]= True
        app.config["TESTING"]= True
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///:memory:'
     
        return app

    def setUp(self):
        db.create_all()
        jordan = User(firstname = "Jordan",lastname = "Williams",email = "jordan2@gmail.com",password = "12345678")
        db.session.add(jordan)
        
        db.session.commit()

    def tearDown(self):
        # pass
        db.session.remove()
        db.drop_all()

class FlaskTestCase(BaseTestCase):

    def test_secure_for_status(self):
        
        response = self.client.get("/secure")
        self.assertEqual(response.status_code,401)

    def test_no_token(self):
        # print(User.query.all())
        response = self.client.get("/secure")
        self.assertEqual(json.loads(response.data),{'code': 'authorization_header_missing', 'description': 'Authorization header is expected'})
    
    def test_add_to_db(self):
        
        response = self.client.post("/register",data=json.dumps(dict(firstname = "John",lastname = "Smith",email = "johnsmith@gmail.com",password = "12345678")),content_type='application/json')
        # print(User.query.all())
        self.assertEqual(json.loads(response.data),{"success": True})

    def test_add_incorrect_email(self):
        
        response = self.client.post("/register",data=json.dumps(dict(firstname = "John",lastname = "Smith",email = "johnsmithgmail.com",password = "12345678")),content_type='application/json')
        self.assertEqual(json.loads(response.data),{'email': ['value does not match regex '"'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$'"]})
    
    def test_get_token(self):
        

        
       
        response = self.client.post("/login",data=json.dumps(dict(email = "jordan2@gmail.com",password = "12345678")),content_type='application/json')
        self.assertEqual(response.status_code,200)

    


if __name__ == "__main__":
    unittest.main()