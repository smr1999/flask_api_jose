from flask.views import MethodView
from flask_smorest import abort,Blueprint

from schemas import ItemSchema,ItemUpdateSchema

from flask_jwt_extended import jwt_required, get_jwt

from sqlalchemy.exc import SQLAlchemyError
from models import ItemModel
from db import db

blp = Blueprint("item" , __name__ , description = "Operations on items")

@blp.route("/item/<int:item_id>")
class Item(MethodView):
    
    @blp.response(200,ItemSchema)
    def get(self,item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item
        
    @jwt_required()
    def delete(self, item_id):
        jwt = get_jwt()

        if not jwt.get("is_admin"):
            abort(
                401, 
                message = "Admin privilege required."
            )

        item = ItemModel.query.get_or_404(item_id)
        
        db.session.delete(item)
        db.session.commit()

        return {
            "message" : "Item has deleted."
        }

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200,ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get_or_404(item_id)

        item.name = item_data["name"]
        item.price = item_data["price"]
        
        db.session.add(item)
        db.session.commit()

        return item 

@blp.route("/item")
class ItemList(MethodView):

    @blp.response(200,ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201,ItemSchema)
    def post(self,item_data):
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, "An error occurred in insertion item in database.")

        return item