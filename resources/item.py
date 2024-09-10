
from flask_jwt_extended import jwt_required,get_jwt
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from schemas import ItemSchema,ItemUpdateSchema
from sqlalchemy.exc import SQLAlchemyError
from models import ItemModel


blp = Blueprint("item",__name__,description="Operations on stores")


@blp.route('/item/<int:item_id>')
class Items(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item=ItemModel.query.get_or_404(item_id)
        return item
    
    @jwt_required()
    def delete(self,item_id):
        jwt=get_jwt()
        if not jwt.get("is_admin"):
            abort(401,message="admin privilege required")
        item=ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message":"Item Deleted"},200
    
    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200,ItemSchema)
    def put(self,item_data,item_id):
        item=ItemModel.query.get(item_id)
        if item:
            item.price=item_data['price']
            item.name=item_data['name']
        else:
            item=ItemModel(item_id=item_id**item_data)

        db.session.add(item)
        db.session.commit()
        return item
@blp.route('/item')
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()
    
    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201,ItemSchema)
    def post(self,item_data):
        item= ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="An error occured while inserting an item")
        return item

    