from app import app,db
from flask import render_template,jsonify,request,make_response
from .models import User,Event
from sqlalchemy import exc
import jwt
from functools import wraps
from cerberus import Validator
from werkzeug.security import generate_password_hash,check_password_hash
import datetime


def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = None
    if "x-access-token" not  in request.headers:
            return jsonify({'code': 'x-access-token_missing', 'description': 'x-access-token header is expected'}), 401

    token = request.headers.get('x-access-token',None)
    
    if not token:
      return jsonify({"Message":"Missing Tokenn"}),401

    
    
    try:
         payload = jwt.decode(token, app.config["SECRET_KEY"])
         current_user = User.query.filter_by(email=payload["email"]).first()
    except jwt.ExpiredSignature:
        return jsonify({'code': 'token_expired', 'description': 'token is expired'}), 401
    except jwt.DecodeError:
        return jsonify({'code': 'token_invalid_signature', 'description': 'Token signature is invalid'}), 401

    # g.current_user = user = payload
    return f(current_user,*args, **kwargs)

  return decorated

@app.route('/register',methods = ['POST'])
def register():

    data = request.json # data from request

    schema = {
    "firstname" : {'type': 'string'},
	"lastname" : {'type': 'string'},
	"email" :  {'type': 'string','regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'},
	"password" : {'type': 'string','minlength': 6, 'maxlength': 20}
	
     }
    v = Validator(schema,require_all=True)
    check = v.validate(data)

    if not check:
        return jsonify(v.errors)

    
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    email = data.get("email")
    password = generate_password_hash(data.get("password"),method="sha256")
    user = User(firstname=firstname,lastname =lastname,email=email,password=password )
    try:
        db.session.add(user)
        db.session.commit()
    except exc.IntegrityError as e:
        return jsonify({"error": "invalid email"}), 409
    return jsonify({"success": True}), 201

@app.route('/login',methods = ['GET'])
def login():
    """Validates a users login and returns a token if true"""
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('User verification failed', 401, {'WWW-Authenticate':'Basic realm="Login Required!"'})

    user = User.query.filter_by(email=auth.username).first()
    
    if not user:
        return jsonify({"error": "invalid email or password"}), 401

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({
            'email':user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
            }, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')}),200

    
    return make_response('User verification failed', 401, {'WWW-Authenticate':'Basic realm="Login Required!"'})

@app.route("/secure",methods=["GET","POST"])
@token_required
def secure(current_user):
    return jsonify({"data": "blah blah"})