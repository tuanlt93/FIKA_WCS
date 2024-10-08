from config.constants import MarkemConfig
from config.config_apis import ConfigAPI
from db_redis import redis_cache
from utils.threadpool import Worker
import json
import requests

class PrintDatamax():
    def __init__(self) -> None:
        super().__init__()
        self.__redis_cache = redis_cache
        self.__redis_pubsub = redis_cache.get_connection().pubsub()
        self.__redis_pubsub.subscribe(MarkemConfig.TOPIC_MARKEM_PRINTER_RESULTS)
        self.__sub_print_request()
        self.__url  = ConfigAPI.url_show_data_temp_print
    
    @Worker.employ
    def __sub_print_request(self):
        print("START PRINT MARKEM")
        while True:
            for message in self.__redis_pubsub.listen():
                if message['type'] == 'message':
                    self.print(message["data"])

    def print(self, message):
        if message == MarkemConfig.MESSAGE_PRINTED_WRONG:
            data_print_json = self.__redis_cache.get(MarkemConfig.DATA_PRINT_SHOW)
            data_print = json.loads(data_print_json)
            requests.post(url= self.__url, json= data_print)
            
            



