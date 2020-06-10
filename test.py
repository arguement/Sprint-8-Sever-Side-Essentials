import unittest
from flask_testing import TestCase
from app import app,db
from app.models import User,Event
import json

import base64
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
from io import BytesIO, StringIO
import os
# from _io import StringIO
from werkzeug.datastructures import FileStorage


def pwrd(password):
    return generate_password_hash(password, method="sha256")

class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        app.config["DEBUG"]= True
        app.config["TESTING"]= True
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///:memory:'
     
        return app

    def setUp(self):
        db.create_all()
        jordan = User(firstname = "Jordan",lastname = "Williams",email = "jordan2@gmail.com",password = generate_password_hash("12345678", method="sha256"))
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
        db.session.add(jordan)
        
        db.session.commit()

    def tearDown(self):
        # pass
        db.session.remove()
        db.drop_all()

        # remove all test files
        file = os.path.join(
            app.config['UPLOAD_FOLDER'], "img1.jpg"
        )
        if os.path.isfile(file):
            os.remove(file)

        file = os.path.join(
            app.config['UPLOAD_FOLDER'], "img2.jpg"
        )
        if os.path.isfile(file):
            os.remove(file)
        

class FlaskTestCase(BaseTestCase):
    
    def test_add_to_db(self):
        
        # response = self.client.post("/register",data=dict(firstname = "John",lastname = "Smith",email = "johnsmith@gmail.com",password = "12345678"),content_type='application/json')
        response = self.client.post('/user',content_type='application/json', 
                                    data=json.dumps(dict(firstname = "John",lastname = "Smith",email = "johnsmith@gmail.com",password = "12345678")))
        
        self.assertEqual(json.loads(response.data),{"success": True})

   
    def test_get_token(self):

       
        response = self.client.open("/login",
            method="POST",
            headers={
                'Authorization': 'Basic ' + base64.b64encode(bytes("jordan2@gmail.com" + \
                ":" + "12345678",'ascii')).decode('ascii')
            })
        dict_data = self.get_token("jordan2@gmail.com","12345678")
        self.assertEqual(response.status_code,200) # 200 means it was successful
        self.assertIsInstance(dict_data, dict) # token is a dictionary aka json
        self.assertIn("token",dict_data) # token is a key in the dictionary

    def get_token(self,username,password):
        response = self.client.open("/login",
            method="POST",
            headers={
                'Authorization': 'Basic ' + base64.b64encode(bytes(username + \
                ":" + password,'ascii')).decode('ascii')
            })
        dict_data = json.loads(response.data)
        return dict_data
    
    def get_file(self,filen,filetype,newname):
    #     my_file = FileStorage(
    #     stream=open(os.path.join(r"app\static\test_images", "dashboard.PNG"), 'rb'),
    #     filename="img1.jpg",
    #     content_type="jpg",
    # )
        TEST_UPLOAD_FOLDER=r"app\static\test_images"
       
        file = FileStorage(
            stream=open(os.path.join(TEST_UPLOAD_FOLDER, filen), 'rb'),
            filename=newname,
            content_type=filetype,
        )
        return file
        


    def test_get_events(self):
        response_with_token = self.get_token("h.potter@hogwarts.com","wizard")
        response = self.client.get('/user',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })
        self.assertEqual(json.loads(response.data),{'code': 'admin_only', 'description': 'Only admins can use this route'}) # non admin cant access all events

        response_with_token = self.get_token("jwick@thecontinental.com","gunner")
        response = self.client.get('/user',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })
        
        self.assertIsInstance(json.loads(response.data),dict) # admin events respoonse

    def test_getUser(self):
        response_with_token = self.get_token("jwick@thecontinental.com","gunner")
        response = self.client.get('/user/3',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })
        
        self.assertIsInstance(json.loads(response.data),dict)
        self.assertEqual(response.status_code,200)

        response = self.client.get('/user/30',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })
        self.assertEqual(response.status_code,404)

    def test_makeAdmin(self):
        response_with_token = self.get_token("jwick@thecontinental.com","gunner")
        response = self.client.put('/user/3',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })
        
        self.assertIsInstance(json.loads(response.data),dict)
        self.assertEqual(response.status_code,200)

        response = self.client.put('/user/30',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })
        self.assertEqual(response.status_code,404)

    def test_deleteUser(self):
        response_with_token = self.get_token("jwick@thecontinental.com","gunner")
        response = self.client.delete('/user/3',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })
        
        self.assertIsInstance(json.loads(response.data),dict)
        self.assertEqual(response.status_code,200)

        response = self.client.delete('/user/30',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })
        self.assertEqual(response.status_code,404)

    def test_create_event(self):
        response_with_token = self.get_token("jwick@thecontinental.com","gunner")
        
    #     my_file = FileStorage(
    #     stream=open(os.path.join(r"app\static\test_images", "dashboard.PNG"), 'rb'),
    #     filename="img1.jpg",
    #     content_type="jpg",
    # )
        my_file = self.get_file("dashboard.PNG","jpg","img2.jpg")

        print(response_with_token)
        response = self.client.post('/event',content_type='multipart/form-data', 
                                        data={"title" : "new event",
                                                "description": "scdscscdccsdc",
                                                "category" : "new category",
                                                "start_date" : "2019-10-06 10:20:03",
                                                "end_date" : "2019-10-06 10:20:03",
                                                "cost" : 2000,
                                                "venue" : "some venue",
                                                "flyer" : my_file},
                                                headers={
                    'x-access-token': response_with_token["token"]
            })
        
        my_file.close()
        self.assertTrue(response.status_code,201)

        my_file = self.get_file("dashboard.PNG","jpg","img2.jpg")

        response = self.client.post('/event',content_type='multipart/form-data', 
                                        data={"title" : "new event",
                                                "description": "scdscscdccsdc",
                                                "category" : "new category",
                                                "start_date" : "2019-10-06 10:20:03",
                                                "end_date" : "2019-10-06 10:20:03",
                                                "flyer" : my_file},
                                                headers={
                    'x-access-token': response_with_token["token"]
            })
        my_file.close()
        dict_data = json.loads(response.data)
        self.assertIsInstance(dict_data, dict) 
        self.assertIn("errors",dict_data) 
    
    def test_get_user(self):
        response_with_token = self.get_token("jwick@thecontinental.com","gunner")
        response = self.client.get('/user',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })
        
        self.assertIsInstance(json.loads(response.data),dict)
        self.assertEqual(response.status_code,200)

    
    def test_get_event(self):
        response_with_token = self.get_token("jwick@thecontinental.com","gunner")
        response = self.client.get('/event/3',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })
        self.assertEqual(response.status_code,200)

        response_with_token = self.get_token("keffs@gmail.com", "kyeeks")
        response = self.client.get('/event/2',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })

        self.assertEqual(response.status_code,403)
    
    def test_get_all_events(self):
        response_with_token = self.get_token("jwick@thecontinental.com","gunner")
        response = self.client.get('/event',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })

        self.assertEqual(response.status_code,200)

    def test_usersEvents(self):
        response_with_token = self.get_token("jwick@thecontinental.com","gunner")
        response = self.client.get('/event/user/1',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })

        dict_data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertIsInstance(json.loads(response.data),dict)
        self.assertIn("events",dict_data)
        self.assertEqual(2,len(dict_data["events"])) #return 2 entriess

    def test_update_event(self):
        response_with_token = self.get_token("jwick@thecontinental.com","gunner")
       


        my_file = self.get_file("testimg2.png","jpg","img3.jpg")
        response = self.client.put('/event/30',content_type='multipart/form-data', 
                                        data={"title" : "new event",
                                                "description": "scdscscdccsdc",
                                                "category" : "new category",
                                                "start_date" : "2019-10-06 10:20:03",
                                                "end_date" : "2019-10-06 10:20:03",
                                                "flyer" : my_file},
                                                headers={
                    'x-access-token': response_with_token["token"]
            })

        my_file.close()
        dict_data = json.loads(response.data)
        
        self.assertEqual(dict_data,{'errors':'event doesnt exist'})
        
        # response = self.client.put('/event/1',content_type='multipart/form-data', 
        #                                 data={"title" : "new event",
        #                                         "description": "scdscscdccsdc",
        #                                         "category" : "new category",
        #                                         "start_date" : "2019-10-06 10:20:03",
        #                                         "end_date" : "2019-10-06 10:20:03",
        #                                         "visibility":"True"},
        #                                         headers={
        #             'x-access-token': response_with_token["token"]
        #     })

        # dict_data = json.loads(response.data)
        # print(dict_data)
        
        # self.assertEqual(dict_data,{'errors':'event doesnt exist'})

    def test_delete_event(self):
        response_with_token = self.get_token("jwick@thecontinental.com","gunner")
        response = self.client.delete('/event/1',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })

        dict_data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)

        response = self.client.delete('/event/300',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })

        dict_data = json.loads(response.data)
        self.assertEqual(response.status_code,404)

        response_with_token = self.get_token("keffs@gmail.com", "kyeeks")
        response = self.client.delete('/event/3',content_type='application/json', headers={
                'x-access-token': response_with_token["token"]
            })

        dict_data = json.loads(response.data)
        self.assertEqual(response.status_code,403)



        


        

        


    


if __name__ == "__main__":
    unittest.main()