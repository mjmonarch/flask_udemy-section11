import hmac
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from models.user import UserModel

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                        type=str,
                        required=True,
                        help="Mandatory parameter: username"
)
_user_parser.add_argument('password',
                        type=str,
                        required=True,
                        help="Mandatory parameter: password"
)

class UserRegister(Resource):

    def post(self):
        data = _user_parser.parse_args()

        # check whether user already exits
        if UserModel.find_by_username(data['username']):
            return {'message': 'User already exists.'}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {'message': 'User created successfully.'}, 201

class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted'}, 200
 
class UserLogin(Resource):

    @classmethod
    def post(cls):
        data = _user_parser.parse_args()

        user = UserModel.find_by_username(data['username'])

        # This is what the 'authenticate()' function used to do
        if user and hmac.compare_digest(user.password, data['password']):
            # identity = is what the 'identity' function used to do
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return {'message': 'Invalid credentials'}, 401
 
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_refresh_token(identity=current_user)
        return {'access_token': new_token}, 200