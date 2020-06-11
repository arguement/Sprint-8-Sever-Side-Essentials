from app import app, db
from flask import render_template, flash, url_for, session, redirect, request, make_response, jsonify
from .models import User, Event
from .forms import RegistrationForm, LoginForm, RegFrontEndForm,EventForm, CreateEventForm, CreateEventForm_Front
from .utils import token_required, form_errors, admin_only, check_for_token
from sqlalchemy import exc, and_, or_
import jwt
from cerberus import Validator
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from werkzeug.utils import secure_filename
import os

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', title="My Main Page")

@app.route('/new_event', methods=['POST', 'GET'])
def create_event_front():
    form = CreateEventForm_Front()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        category = form.category.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        cost = form.cost.data
        venue = form.venue.data
        flyer = form.flyer.data

        filename = secure_filename(flyer.filename)
        flyer.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename
        ))

        event = Event(title=title, description=description, category=category, start_date=start_date, end_date=end_date, cost=cost, venue=venue, flyer=flyer.filename)

        db.session.add(event)
        db.session.commit()
        flash('Event Successfully Created', category='success')

        return redirect(url_for("events"))
    
    return render_template('event.html', title="Create An Event", form=form, user=session['username'], events=events)

@app.route('/myevents', methods=['GET'])
def events_user():
    #current_user =
    events = Event.query.filter(Event.user_id == session['id']).all()

    return render_template('user_events.html', title='My Events', user=session['username'], events=events)

@app.route('/togglevisibility/<event_id>', methods=['GET'])
def events_visibility(event_id):
    #current_user =
    event = Event.query.filter(Event.id == event_id).first()
    event.visibility = not event.visibility
    db.session.commit()
    print("location")
    print(request.referrer)
    if request.referrer == "http://127.0.0.1:5000/events":
        return redirect(url_for("events"))
    return redirect(url_for("events_user"))

@app.route('/events', methods=['GET'])
def events():
    if session['admin']:
        events = Event.query.all()
    else:
        events = Event.query.filter((Event.user_id == session['id']) | (Event.visibility == 1)).all()

    return render_template('events.html', title='Events', user=session['username'], events=events)

@app.route('/users', methods=['GET'])
def user_front():
    users = User.query.all()

    return render_template('users.html', title='Users', user=session['username'], users=users)

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
            session['username'] = user.firstname
            session['id'] = user.id
            session['admin'] = user.admin
            flash('Successfully logged in', category='success')
            return redirect(url_for('events'))
    return render_template('login.html', title='Login', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    
    session.pop('username', None)
    session.pop('admin', None)
    session.pop('id', None)
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
@app.route('/login', methods=['POST','GET'])
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
@admin_only
def get_users():
    """Get a list of all users (including details)"""

    users = User.query.all()
    output = []
    for user in users:
        output.append(user.to_dict(show=["firstname", "lastname", "admin"]))
    return jsonify({'users:': output}),200


@app.route('/user/<user_id>', methods=['GET'])
@token_required
@admin_only
def getUser(user_id):
    """Get information on the user with the given ID"""
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify({'user': user.to_dict(show=["firstname", "lastname", "admin"])}),200
    else:
        return jsonify({'Message':'User does not exist'}),404


@app.route('/user/<user_id>', methods=['PUT'])
@token_required
@admin_only
def makeAdmin(user_id):
    """"Toggles the user with the provided ID to an admin or not admin"""
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.admin=True
        db.session.commit()
        return jsonify({'Message':f'User with email {user.email} promoted to admin'}),200
    else:
        return jsonify({'Message':'User does not exist'}),404


@app.route('/user/<user_id>', methods=['DELETE'])
@token_required
@admin_only
def deleteUser(user_id):
    """Deletes the user with given ID"""

    user = User.query.filter_by(id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'Message':f'User with email {user.email} deleted'}),200
    else:
        return jsonify({'Message':'User does not exist'}),404


@app.route('/event', methods=['POST'])
@token_required
def create_event(current_user):
    """Create a new event"""
    # data = request.json     # results from json request
    form = CreateEventForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        category = form.category.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        cost = form.cost.data
        venue = form.venue.data
        flyer = form.flyer.data

        filename = secure_filename(flyer.filename)
        flyer.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename
        ))

        event = Event(user = current_user,title = title, description = description, category = category, start_date = start_date, end_date = end_date, cost = cost, venue = venue, flyer = flyer.filename)
        try:
            db.session.add(event)
            db.session.commit()
        except exc.IntegrityError as e:
            return jsonify({"error": "invalid input"}), 409

        return jsonify({"success": True}), 201
    else:
        return jsonify({'errors':form_errors(form)})


@app.route('/event', methods=['GET'])
@check_for_token
def get_all_events(current_user):
    """Get a list of all (visible) events """

    # if the user is an admin, return all events. Otherwise, only visible events
    if current_user.admin:
        events = Event.query.all()
    else:
        events = Event.query.filter((Event.user_id == current_user.id) | (Event.visibility == 1)).all()


    output = []
    for event in events:
        output.append(event.to_dict(show=["title", "description", "cost", "start_date", "visibility", "user_id", "flyer"]))
    return jsonify({'events': output}),200


@app.route('/event/<event_id>', methods=['GET'])
@check_for_token
def get_event(current_user, event_id):
    """Get details on the event with the given ID"""

    event = Event.query.filter_by(id=event_id).first()

    # check if event exists
    if not event:
        return jsonify({'message': 'Event does not exist.'})

    if current_user.admin:
        pass
    else:
        event = Event.query.filter((Event.id == event_id) &
                ((Event.visibility == True) | (Event.user_id == current_user.id))).first()

    if not event:
        return jsonify({'message': 'You do not have permission to view this event'}),403

    output = []

      
        
    output.append(event.to_dict(show=["title", "description", "cost", "start_date", "visibility", "user_id", "flyer"]))  
    return jsonify({'Event' : output}),200


@app.route('/event/user/<user_id>', methods=['GET'])
@check_for_token
def usersEvents(current_user,user_id):
    """"Get a list of all events created by a particular user. Only admins can get info on any user:
        regular users can only request their own events
    """
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'errors':'user does not exist'})
    elif current_user.admin:
        events = user.event.all()
    elif user.id == current_user.id:
        # User is not an admin, but requesting info on all of his/her events
        events = user.event.all()
    else:
        events = user.event.filter_by(visibility=True).all()
        # return jsonify({'errors':'only admins can view events of another user'})

    if not events:
        return jsonify({'message':'User has no events/no visible events'})

    columns = Event.__table__.columns.keys() # get all column names
    events_data = list(map(lambda x: x.to_dict(show=columns),events))


    return jsonify({'events': events_data}),200


@app.route('/event/<event_id>', methods=['PUT'])
@token_required
def update_event(current_user, event_id):
    """"Update the event with a given ID. Only users who created an event and admins can update it. Additionally, only admins can set the event visibility"""
    data = request.form.to_dict() # data from request
    print(data)
    try:
        form = EventForm()
    except Exception as e:
        return jsonify({"errors": f"{e}"})

    if not form.validate_on_submit():
        return jsonify({'errors':form_errors(form)})

    event = Event.query.filter_by(id=event_id).first()
    if not event:
        return jsonify({'errors':'event doesnt exist'})

    if current_user.admin == False:

        if current_user.id != event.user_id:
            return jsonify({"errors":"you dont have permission to change this event"})

        if "visibility" in data:
            return jsonify({"errors":"user cannot change visibilty"})
    else:
        if "visibility" in data:
            data["visibility"] = True if data["visibility"].lower() == "true" else False

    try:
        # check for new flyer file info
        flyer = form.flyer.data
        filename = secure_filename(flyer.filename)
        flyer.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename
        ))

        #old file info
        file = os.path.join(
            app.config['UPLOAD_FOLDER'], event.flyer
        )
        event.flyer = filename # chaange in db
        if os.path.isfile(file):
            os.remove(file)
        else:    ## Show an error ##
            print("Error: %s file not found" % file)
    except:
        data.pop("flyer", None)

    for k,v in data.items():
        setattr(event,k,v)


    db.session.commit()

    return jsonify({'message':'success'}),200


@app.route('/event/<event_id>', methods=['DELETE'])
@token_required
def delete_event(current_user,event_id):
    """Delete the event with given ID. Only admins or the user who created an event can delete it"""
    event = Event.query.filter_by(id=event_id).first()
    if not event:
        return jsonify({'errors':'event doesnt exist'}),404

    if current_user.admin == False:
        if current_user.id != event.user_id:
            return jsonify({"errors":"you dont have permission to change this event"}),403

    db.session.delete(event)
    db.session.commit()
    return jsonify({'message':'success'}),200