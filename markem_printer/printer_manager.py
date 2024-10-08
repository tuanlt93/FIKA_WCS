from utils.threadpool import Worker
from markem_printer.printer_interface import PrintInterface
from db_redis import redis_cache
from config.constants import MarkemConfig
import threading
import json
class PrintHandle():
    def __init__(self) -> None:
        # super().__init__()
        self.__print_interface = PrintInterface()
        self.__redis_cache = redis_cache
        self.__redis_pubsub = redis_cache.get_connection().pubsub()
        self.__redis_pubsub.subscribe(MarkemConfig.TOPIC_NOTIFY_SEND_DATA_PRINT)
        # self.__sub_print_request()

        background_thread = threading.Thread(target=self.__sub_print_request)
        background_thread.daemon = True
        background_thread.start()
    
    # @Worker.employ
    def __sub_print_request(self):
        print("START PRINT MARKEM")
        while True:
            for message in self.__redis_pubsub.listen():
                if message['type'] == 'message':
                    self.print(message["data"])

    def print(self, message):
        if message :
            data_print = self.__redis_cache.get_first_element(key= MarkemConfig.DATA_CARTON_LABLE_PRINT)
            print(data_print)
            self.__redis_cache.set(MarkemConfig.DATA_PRINT_SHOW, json.dumps(data_print))
            self.__print_interface.send_data_print_lable(data_print)
            self.__redis_cache.delete_first_element(key= MarkemConfig.DATA_CARTON_LABLE_PRINT)
            
            



