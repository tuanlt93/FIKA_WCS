from flask import Flask
from flask_jwt_extended import JWTManager
from flask_babel import Babel
from flask_cors import CORS
from utils.logger import Logger
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

        # INIT REST API
        self._count_api = 0
        api.init_app(self.app)



    def start(self):
        """ RUN FLASK
        """
        Logger().info("RestAPI READY")
        self._count_api = self._count_api + 1
        # print("count ", self._count_api)
        if self._count_api > 2:
            Logger().error("Server API not right")
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
    

