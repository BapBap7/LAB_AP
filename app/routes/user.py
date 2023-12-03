from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from app import db
from app.models.models import User


user_blueprint = Blueprint('user', __name__)
bcrypt = Bcrypt()


@user_blueprint.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'User with this email already exists'}), 409

    new_user = User(email=email, username=username, password=hashed_password)

    # Add the user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201


@user_blueprint.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)

    if user:
        user_data = {
            'id': user.id,
            'email': user.email,
            'username': user.username

        }
        return jsonify({'user': user_data}), 200
    else:
        return jsonify({'message': 'User not found'}), 404
