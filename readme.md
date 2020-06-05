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