from utils.threadpool import Worker
from config.constants import SorterConfig
from db_redis import redis_cache
from PLC import PLC_controller

class SorterHandle():
    def __init__(self) -> None:

        self.__PLC_controller = PLC_controller
        self.__redis_pubsub = redis_cache.get_connection().pubsub()
        self.__redis_pubsub.subscribe(SorterConfig.TOPIC_STT_CARTON_AFTER_INSPECTION)
        self.__sub_value_sorter()
    
    @Worker.employ
    def __sub_value_sorter(self):
        while True:
            for message in self.__redis_pubsub.listen():
                if message['type'] == 'message':
                    self.send_data_print_lable(message["data"])

    def send_data_print_lable(self, message):
        if message:
            print("DATA SORTER")
            print(message)
            index_of_semicolon = message.find(';')
            if index_of_semicolon > 0:  # Đảm bảo có ký tự trước dấu ';'
                char_before_semicolon = message[index_of_semicolon - 1]
                if char_before_semicolon == "1":
                    self.__PLC_controller.request_sort_ng()
                if char_before_semicolon == "0":
                    self.__PLC_controller.request_sort_ok()
                self.__PLC_controller.done_request_sort()
                print("DONE SORTER")
            else: 
                print("NO DATA")

            
            



