from app import app, db
from flask import render_template, flash, url_for, session, redirect, request, make_response, jsonify
from .models import User, Event
from .forms import RegistrationForm, LoginForm, RegFrontEndForm,EventForm
from .utils import token_required, form_errors
from sqlalchemy import exc
import jwt
from cerberus import Validator
from werkzeug.security import generate_password_hash, check_password_hash
import datetime


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', title="My Main Page")

@app.route('/events', methods=['GET'])
def events():
    events = Event.query.all()
    return render_template('events.html', title='Events', user=session['user'], events=events)

@app.route('/login-front', methods=['POST', 'GET'])
def login_front():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Credentials incorrect', category='danger')
            return redirect(url_for('login_front'))
        if check_password_hash(user.password, password):
            session['user'] = user.firstname
            flash('Successfully logged in', category='success')
            return redirect(url_for('events'))
    return render_template('login.html', title='Login', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user', None)
    flash('You have logged out successfully', category='success')
    return redirect(url_for('login_front'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegFrontEndForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        password = form.password.data

        user = User(firstname=firstname, lastname=lastname, email=email, password=generate_password_hash(password, method='sha256'))

        db.session.add(user)
        db.session.commit()
        flash('Successfully Registered', category='success')
        return redirect(url_for('index'))
    
    return render_template('register.html', title="Register", form=form)



#=========================== REST API ===============================
@app.route('/login', methods=['GET'])
def login():
    """ Logs in a user and returns a JWT Token """

    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('User verification failed', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})

    user = User.query.filter_by(email=auth.username).first()

    if not user:
        return jsonify({"error": "invalid email or password"}), 401

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({
            'email': user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')}), 200

    return make_response('User verification failed', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})


@app.route('/user', methods=['POST'])
def createUser():
    """ Creates a new user (registers the user) """
    data = request.json  # data from request
    form = RegistrationForm.from_json(data)

    if form.validate_on_submit():
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        email = data.get("email")
        password = generate_password_hash(data.get("password"), method="sha256")
        user = User(firstname=firstname, lastname=lastname,
                    email=email, password=password)
        try:
            db.session.add(user)
            db.session.commit()
        except exc.IntegrityError as e:
            return jsonify({"error": "invalid email"}), 409

        return jsonify({"success": True}), 201
    else:
        return jsonify({'errors':form_errors(form)})


@app.route('/user', methods=['GET'])
@token_required
def get_users(current_user):
    """Get a list of all users (including details)"""
    if not current_user.admin:
        return jsonify({'Message':'Sorry, function not permitted!'}), 401

    users = User.query.all()
    output = []
    for user in users:
        output.append(user.to_dict(show=["firstname", "lastname", "admin"]))
    return jsonify({'users:': output})


@app.route('/user/<user_id>', methods=['GET'])
# @token_required
def getUser(user_id):
    """Get information on the user with the given ID"""
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify({'user': user.to_dict(show=["firstname", "lastname", "admin"])})
    else:
        return jsonify({'Message':'User does not exist'})


@app.route('/user/<user_id>', methods=['PUT'])
def makeAdmin(user_id):
    """"Toggles the user with the provided ID to an admin or not admin"""
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.admin=True
        db.session.commit()
        return jsonify({'Message':f'User with email {user.email} promoted to admin'})
    else:
        return jsonify({'Message':'User does not exist'})


@app.route('/user/<user_id>', methods=['DELETE'])
@token_required
def deleteUser(current_user, user_id):
    """Deletes the user with given ID"""
    if not current_user.admin:
        return jsonify({'Message':'Sorry, function not permitted!'}), 401

    user = User.query.filter_by(id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'Message':f'User with email {user.email} deleted'})
    else:
        return jsonify({'Message':'User does not exist'})


@app.route('/event', methods=['GET'])
def create_event():
    """Create a new event"""
    pass


@app.route('/event', methods=['GET'])
def get_all_events():
    """Get a list of all (visible) events """
    pass


@app.route('/event/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get details on the event with the given ID"""
    pass


@app.route('/event/user/<user_id>', methods=['GET'])
def usersEvents(user_id):
    """"Get a list of all events created by a particular user"""
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'errors':'user doesnt exist'})
    
    events = user.event.all()
    columns = Event.__table__.columns.keys() # get all column names
    events_data = list(map(lambda x: x.to_dict(show=columns),events))
    
    
    return jsonify({'events': events_data}),200
    

@app.route('/event/<event_id>', methods=['PUT'])
@token_required
def update_event(current_user, event_id):
    """"Update the event with a given ID. Only users who created an event and admins can update it. Additionally, only admins can set the event visibility"""
    data = request.json  # data from request
    
    try:
        form = EventForm.from_json(data,skip_unknown_keys=False)
    except Exception as e:
        return jsonify({"errors": f"{e}"})

    if not form.validate_on_submit():
        print("here")
        return jsonify({'errors':form_errors(form)})

    event = Event.query.filter_by(id=event_id).first()
    if not event:
        return jsonify({'errors':'event doesnt exist'})

    if current_user.admin == False:
        
        if current_user.id != event.user_id:
            return jsonify({"errors":"you dont have this event"})

        if "visbility" in data:
            return jsonify({"errors":"user cannot change visibilty"})

        for k,v in data.items():
            setattr(event,k,v)

    else:
        for k,v in data.items():
            setattr(event,k,v)


    db.session.commit()

    return jsonify({'message':'success'}),200


@app.route('/event/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete the event with given ID"""
    event = Event.query.filter_by(id=event_id).first()
    if not event:
        return jsonify({'errors':'event doesnt exist'})

    db.session.delete(event)
    db.session.commit()
    return jsonify({'message':'success'}),200
    

@app.route("/secure", methods=["GET", "POST"])
@token_required
def secure(current_user):
    return jsonify({"data": "blah blah"})
