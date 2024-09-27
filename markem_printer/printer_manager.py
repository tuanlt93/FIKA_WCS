from utils.threadpool import Worker
from markem_printer.printer_interface import PrintInterface
from db_redis import redis_cache
from config.constants import MarkemConfig


class PrintHandle(PrintInterface):
    def __init__(self) -> None:
        super().__init__()
        self.__redis_cache = redis_cache
        self.__redis_pubsub = redis_cache.get_connection().pubsub()
        self.__redis_pubsub.subscribe(MarkemConfig.TOPIC_NOTIFY_SEND_DATA_PRINT)
        self.__sub_print_request()
    
    @Worker.employ
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
            self.send_data_print_lable(data_print)
            self.__redis_cache.delete_first_element(key= MarkemConfig.DATA_CARTON_LABLE_PRINT)
            
            



