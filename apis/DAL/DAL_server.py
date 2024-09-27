from utils.pattern import Singleton
import requests
# from utils.logger import Logger
from db_redis import redis_cache
from config.constants import HandlePalletConfig
from config.config_apis import ConfigAPI


class DALServer(metaclass=Singleton):
    """
    A singleton handle DAL logic
    """

    def __init__(self):
        """
            Get token bearer from backend
        """
        # self.__account      = self.__get_account()
        # self.__token_value  = self.__get_token_bearer_backend(self.__account)
        self.__token_value =  {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWRtaW4iLCJyb2xlIjoiQWRtaW4iLCJpYXQiOjE3Mjc0MDI5NDMsImV4cCI6MTc1ODUwNjk0M30.SHngUPOqe7aJPhqwc0hx_ZEgSdFwZOOhikBxzVafR_E'}

    def __get_token_bearer_backend(self, cfg: dict) -> dict:
        """
            get token backend
        """
        request_body = {"name": cfg["name"], "password": str(cfg["pass"])}
        try:
            # res = requests.post(cfg["url"] + cfg["login"], json=request_body, timeout=3)
            url = ConfigAPI.url + ConfigAPI.login
            res = requests.post(url, json=request_body, timeout=3)
            response = res.json()
            token_request = {
                "Authorization": "Bearer {}".format(
                    response["metaData"]["access_token"]
                )
            }
            return token_request
        except Exception as e:
            print("e :", e)
            pass

    def __get_account(self) -> dict:
        account = {
            "name"      : "admin",
            "pass"      : "123456"
        }
        return account

    def get_token_bearer(self):
        # print(self.__token_value)
        return self.__token_value
    

