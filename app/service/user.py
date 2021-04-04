from app.models.user import User
from . import cloudapp
from app import db
from flask import request, jsonify
from flask_login import login_required, current_user
from password_validation import PasswordPolicy


@cloudapp.route("/user", methods=['POST'])
def register():
    # create a new user
    username = request.json.get("username")
    password = request.json.get("password")
    if username is None or password is None:
        return jsonify({"error": "The input is not valid."}), 404
    elif User.query.filter_by(username=username).first():
        return jsonify({"error": "The username already exists."}), 404
    policy = PasswordPolicy()
    if policy.validate(password):      
        new_user = User()
        new_user.set_attr(request.json)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Successfully created a new user {}.".format(username)}), 201
    else:
        invalid_items = dict()
        invalid_items['message'] = "The input password is not valid."
        for item in policy.test_password(password):
            invalid_items[item.name] = item.requirement
        return invalid_items, 202       


@cloudapp.route("/user", methods=['GET'])
@login_required
def get_user():
    # retrieve the user's information
    user = User.query.filter_by(id=current_user.id).first()
    if user:
        return jsonify({"message": "Current user is {}".format(user.username)}), 200
    else:
        return jsonify({"message": "You are unauthorized to do the operation."}), 401


@cloudapp.route("/user/authInfo", methods=['PUT'])
@login_required
def modify_password():
    # update the user password
    update_password = request.json.get("password")
    policy = PasswordPolicy()
    if policy.validate(update_password):
        current_user.password = update_password
        db.session.commit()
        return jsonify({"message": "Successfully updated the password."}), 200
    else:
        invalid_items = dict()
        invalid_items['message'] = "The input password is not valid."
        for item in policy.test_password(update_password):
            invalid_items[item.name] = item.requirement
        return invalid_items, 202
