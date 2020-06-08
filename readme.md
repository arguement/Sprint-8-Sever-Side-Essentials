# Event Management System - Sprint 8
**Order1.EXE - Developers**
* Daniel Campbell
* Nathaniel Christie
* Kayla Effs
* Lanai Nevers
* Jordan Williams

Remember to always create a virtual environment and install the packages in your requirements file

```
$ python -m venv venv
$ source venv/bin/activate (or .\venv\Scripts\activate on Windows)
$ pip install -r requirements.txt 
$ python run.py
```

## Running Flask-Migrate
Once your database is set up (preferably as above), run these commands

```
python flask-migrate.py db init
python flask-migrate.py db migrate
python flask-migrate.py db upgrade
```

If you wish to update your database model, modify the [models.py](app\models.py) file, then run:

```
python flask-migrate.py db migrate
python flask-migrate.py db upgrade
```

---

## Useful functions
Credit to <https://wakatime.com/blog/32-flask-part-1-sqlalchemy-models-to-json> for this  
Check their site for more details and usage

Two functions have been added to all model classes as follows
```Py
# Shows some default properties of a model, plus additional fields specified with show
model.to_dict(show=None, _hide=[], _path=None)

# Updates all the fields specified in the dict.
model.from_dict(**some_dict)
```

**Example using the user model**
```Py

u1 = User.query.first()

# return dictionary with the default fields + specified fields for this user
u1.to_dict(show=['firstname', 'lastname', 'event'])

# update some attributes for this user
dt = {'firstname':'John','lastname':'Wick'}
# returns a dictionary pair the old and new values of altered fields
u1.from_dict(**dt)

```

## Initializing Your Database Tables with Users and Events
To get a fresh database with some Users and Events initialized, use the following command:
```
python db_init.py
```
