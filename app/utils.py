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

        # g.current_user = user = payload
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