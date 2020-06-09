from flask import request, jsonify, make_response
from functools import wraps
from app import db, app
from app.models import User, Event

import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "x-access-token" not in request.headers:
            return jsonify({'code': 'x-access-token_missing', 'description': 'x-access-token header is expected'}), 401

        token = request.headers.get('x-access-token', None)

        if not token:
            return jsonify({"Message": "Missing Tokenn"}), 401

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"])
            current_user = User.query.filter_by(email=payload["email"]).first()
        except jwt.ExpiredSignature:
            return jsonify({'code': 'token_expired', 'description': 'token is expired'}), 401
        except jwt.DecodeError:
            return jsonify({'code': 'token_invalid_signature', 'description': 'Token signature is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def admin_only(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        # user authenticated from login required
        if current_user.admin:
            return f(*args, **kwargs)
        else:
            return jsonify({'code': 'admin_only', 'description': 'Only admins can use this route'}), 401
    return decorated
    
def check_for_token(f):
    """Determines if the user has a valid token for logged in priviledges: otherwise use guest account"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        guest = User(firstname="", lastname="", email="", password="", admin=False, id=0)
        if "x-access-token" in request.headers:
            token = request.headers.get('x-access-token', None)

            if token:
                try:
                    payload = jwt.decode(token, app.config["SECRET_KEY"])
                    current_user = User.query.filter_by(email=payload["email"]).first()
                except:
                    current_user = guest
            else:
                current_user = guest
        else:
            current_user = guest

        return f(current_user, *args, **kwargs)

    return decorated

def form_errors(form):
    """Collects and returns a list of form errors"""
    error_messages = []
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            )
            error_messages.append(message)

    return error_messages