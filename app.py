from flask import Flask, jsonify
from flask_migrate import Migrate, upgrade
import os
from flask_smorest import Api
from db import db
from flask_jwt_extended import JWTManager
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources import UserBlueprint
from blocklist import BLOCKLIST
def create_app(db_url=None):
    app= Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"]=True
    app.config["API_TITLE"]='STORES REST API'
    app.config['API_VERSION']='v1'
    app.config['OPENAPI_VERSION']='3.0.3'
    app.config['OPENAPI_URL_PREFIX']='/'
    app.config['OPENAPI_SWAGGER_UI_PATH']='/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL']='https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/'
    app.config['SQLALCHEMY_DATABASE_URI']= db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    app.config['JWT_SECRET_KEY']="junaid"  # use this in terminal import secrets secrets.SystemRandom().getrandbits(128) and assign this value to secret key
    db.init_app(app)
    migrate=Migrate(app,db)
    api=Api(app)
    jwt=JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_token_in_blocklist(jwt_header,jwt_payload):
        return jwt_payload['jti'] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header,jwt_payload):
        return (
            jsonify ({"description":"token has been revoked","error":"token_revoked"}),401
        )
    
    @jwt.additional_claims_loader
    def add_claims(identity):
            #look into database and check if user is admin or not ,etc
        if identity==1:
            return {"is_admin":True}
        return {"is_admin":False}
    @jwt.expired_token_loader
    def expired_token_call(jwt_header,jwt_payload):
        return (
            jsonify( {"message":"The token has expired","error":"token_expired"}),401
        )
    
    @jwt.invalid_token_loader
    def invalid_token_call(error):
        return (
            jsonify({"message":"Signature verification failed","error":"invalid_token"}),401
        )
    
    @jwt.unauthorized_loader
    def missing_token_call(error):
        return (
            jsonify({"message":"Request does not conatain access token","error":"authorisation_error"}),401
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header,jwt_payload):
        return (
            jsonify({
                "description":"The token is not fresh",
                "error":"fresh_token_Required"
            }),401
        )
    with app.app_context():
        upgrade()
    #     db.create_all()
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    return app