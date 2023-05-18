from flask.views import MethodView
from flask_smorest import abort,Blueprint

from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from db import db
from models import StoreModel

from schemas import StoreSchema

blp = Blueprint("store" , __name__ , description = "Operations on stores")

@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200,StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        
        return store

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        
        db.session.delete(store)
        db.session.commit()

        return {
            "message" : "Store has deleted."
        }

@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200,StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self,store_data):
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, 
                  message= "A store with this name already exists"
            )
        except SQLAlchemyError:
            abort(500, 
                  message= "An error while inserting store in the database"
            )

        return store