from datetime import timedelta

from flask.views import MethodView
from flask_smorest import abort,Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, create_refresh_token, get_jwt_identity

from schemas import UserSchema

from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from models import UserModel
from db import db

from blocklist import BLOCKLIST

blp = Blueprint("user" , __name__ , description = "Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        try:
            user = UserModel(
                username = user_data["username"],
                password = generate_password_hash(user_data["password"])
            )
            db.session.add(user)
            db.session.commit()
        
        except IntegrityError:
            return abort(
                409, message= "User with this username exists."
            )

        return {
            "message" : "User created successfully."
        }, 201
    
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and check_password_hash(user.password, user_data["password"]):
            access_token = create_access_token(
                identity=user.id, fresh=True
            )
            refresh_token = create_refresh_token(
                identity= user.id
            )
            return {
                "access_token" : access_token,
                "refresh_token" : refresh_token
            }, 200
        
        abort(
            404,
            message="Invalid credentials."
        )

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user,fresh=False)

        """
        if we want use refresh-token once
        jti = get_jwt()["jti"]
        BLOCKLIST.set(jti, "")
        """

        return {
            "access_token" : new_token
        }


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.set(jti, "", ex=timedelta(minutes=15))

        return {
            "message" : "successfully logged out."
        }, 200

    
@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        db.session.delete(user)
        db.session.commit()

        return {
            "message" : "User deleted."
        }, 200