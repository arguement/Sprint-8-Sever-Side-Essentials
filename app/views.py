from app import app,db
from flask import render_template,jsonify,request
from .models import User,Event
from sqlalchemy import exc
import jwt
from functools import wraps
from cerberus import Validator

def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.headers.get('Authorization', None)
    if not auth:
      return jsonify({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'}), 401

    parts = auth.split()

    if parts[0].lower() != 'bearer':
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}), 401
    elif len(parts) == 1:
      return jsonify({'code': 'invalid_header', 'description': 'Token not found'}), 401
    elif len(parts) > 2:
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}), 401

    token = parts[1]
    try:
         payload = jwt.decode(token, app.config["SECRET_KEY"])

    except jwt.ExpiredSignature:
        return jsonify({'code': 'token_expired', 'description': 'token is expired'}), 401
    except jwt.DecodeError:
        return jsonify({'code': 'token_invalid_signature', 'description': 'Token signature is invalid'}), 401

    # g.current_user = user = payload
    return f(*args, **kwargs)

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
    password = data.get("password")
    user = User(firstname=firstname,lastname =lastname,email=email,password=password )
    try:
        db.session.add(user)
        db.session.commit()
    except exc.IntegrityError as e:
        return jsonify({"error": "invalid email"}), 409
    
    return jsonify({"success": True}), 201

@app.route('/login',methods = ['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    check = User.query.filter_by(email=email,password=password).first()
    if not check:
        return jsonify({"error": "invalid email or password"}), 409

    payload = {'email': email,"password":password}
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm='HS256').decode('utf-8')
    return jsonify(error=None, data={'token': token}, message="Token Generated"), 200

@app.route("/secure",methods=["GET","POST"])
@token_required
def secure():
    return jsonify({"data": "blah blah"})