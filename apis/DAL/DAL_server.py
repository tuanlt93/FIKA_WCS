from utils.pattern import Singleton
import requests
from config.config_apis import ConfigAPI
from utils.logger import Logger
import time
class DALServer(metaclass=Singleton):
    """
    A singleton handle DAL logic
    """

    def __init__(self):
        """
            Get token bearer from backend
        """
        self.__account = {
            "name"      : "admin",
            "pass"      : "Fika@2024"
        }
        self.__token_value = {}
        self.handle_get_tocken()
        
    def handle_get_tocken(self):
        while not self.get_token_bearer_backend():
            time.sleep(5)

    def get_token_bearer_backend(self) -> bool:
        """
            get token backend
        """
        request_body = {"name": self.__account["name"], "password": str(self.__account["pass"])}
        try:
            url = ConfigAPI.url + ConfigAPI.login
            res = requests.post(url, json=request_body)
            response = res.json()
            token_request = {
                "Authorization": "Bearer {}".format(
                    response["metaData"]["access_token"]
                )
            }
            self.__token_value = token_request
            print(self.__token_value)
            Logger().info("Get token seccessful message.")
        except Exception as e:
            Logger().error(f"Get token error: {e}")
            return False
        return True

    def get_token_bearer(self):
        return self.__token_value
    

