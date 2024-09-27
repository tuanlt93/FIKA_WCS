from flask import Flask
from flask_jwt_extended import JWTManager
from flask_babel import Babel
from flask_cors import CORS

from apis.api_base import api
from database.models.user import DB_RevokedToken
from waitress import serve
from config import CFG_SERVER

class FlaskApp:
    jwt = JWTManager()

    def __init__(self) -> None:
        # INIT APP
        self.app = Flask(__name__)
        self.app.config["CORS_HEADERS"] = "application/json"
        self.cors = CORS(self.app)

        # # INIT JWT
        # self.app.config["JWT_SECRET_KEY"] = "jwt-secret-string"
        # self.app.config["JWT_BLACKLIST_ENABLED"] = True
        # self.app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
        # self.jwt.init_app(self.app)

        # LOADING LANGUAGE FOR ALL USER
        self.app.config["LANGUAGES"] = ["en", "vi", "ko", "ja"]
        self.babel = Babel(self.app)

        # # print(config)
        # self.app.config['REDIS_HOST'] = config["CFG_REDIS"]["host"]
        # self.app.config['REDIS_PORT'] = config["CFG_REDIS"]["port"]
        # self.app.config['REDIS_DB'] = 0
        # self.app.config['REDIS_PASSWORD'] = config["CFG_REDIS"]["password"]
        # redis_handler.init_app(self.app)  

        # config monogodb:
        # self.app.config["MONGO_URI"] = "mongodb://localhost:27017/yourDatabaseName"
        # mongo = PyMongo(self.app) 


        
        # api.addClassResource(DWSHeartBeat)
        # api.addClassResource(DWSResult)


        # INIT REST API
        self._count_api = 0
        api.init_app(self.app)



    def start(self):
        """ RUN FLASK
        """
        print("RestAPI ready")
        self._count_api = self._count_api + 1
        # print("count ", self._count_api)
        if self._count_api > 2:
            print("Server API not right")
            exit(code=-1)
        # flask_cfg['debug'] = True
        # serve(self.app, **flask_cfg)
        # self.app.run(host= "0.0.0.0", port= 5000)

        serve(self.app, **CFG_SERVER)
         

    @staticmethod
    @jwt.token_in_blocklist_loader
    def checkBlocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = DB_RevokedToken.findById(jti)
        if token:
            return True
        return False
    

