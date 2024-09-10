from db import db

class TagModel(db.Model):
    __tablename__="tags"

    tag_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80),unique=True,nullable=False)
    store_id=db.Column(db.Integer,db.ForeignKey("stores.store_id"),nullable=False)

    store=db.relationship("StoreModel",backref=db.backref('tags'))
    item=db.relationship("ItemModel",backref=db.backref('tags'),secondary="item_tag")