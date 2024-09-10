from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from models import TagModel, StoreModel ,ItemModel
from schemas import TagSchema, ItemTagSchema
from sqlalchemy.exc import SQLAlchemyError, IntegrityError



blp = Blueprint("tag",__name__,description="Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200,TagSchema(many=True))
    def get(self, store_id):
        store=StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201,TagSchema)
    def post(self,tag_data,store_id):
        if TagModel.query.filter(TagModel.store_id==store_id,TagModel.name==tag_data['name']).first():
            abort(400,message="A tag with this name already exists in that store")
        tag=TagModel(**tag_data,store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500,message=str(e))
        return tag
    
@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200,TagSchema)
    def get(self,tag_id):
        tag=TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(
        202,
        description="Delete a tag if no item is tagged with it",
        example={"message":"Tag deleted"}
    )
    @blp.alt_response(404,description="Tag not found")
    @blp.alt_response(400,description="Returned if tag is assigned to one or more items.In this case tag is not deleted")
    def delete(self,tag_id):
        tag=TagModel.query.get_or_404(tag_id)

        if not tag.item:
            db.session.delete(tag)
            db.session.commit()
            return {'message':"tag deleted"}
        abort(400, message="Could not delete tag. Make sure tag is not associated with any items. then try again")
    
@blp.route('/item/<int:item_id>/tag/<int:tag_id>')
class LinkTagsToItems(MethodView):
    @blp.response(201,TagSchema)
    def post(self,item_id,tag_id):
        item=ItemModel.query.get_or_404(item_id)
        tag=TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="An Error occured while inserting tag")
        
        return tag
    
    @blp.response(200,ItemTagSchema)
    def delete(self,item_id,tag_id):
        item=ItemModel.query.get_or_404(item_id)
        tag=TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="An Error occured while inserting tag")
        
        return {"message":"item removed from the tag","item":item,"tag":tag}

