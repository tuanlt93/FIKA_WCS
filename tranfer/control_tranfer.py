from utils.threadpool import Worker
from config.constants import SorterConfig
from db_redis import redis_cache
from PLC import PLC_controller
from database import db_connection
from config.constants import HandleCartonConfig
import time
from utils.logger import Logger
from config.settings import TIME

class TranferHandle():
    def __init__(self) -> None:

        self.__PLC_controller = PLC_controller
        self.__db_connection  = db_connection
        self.__redis_pubsub = redis_cache.get_connection().pubsub()
        self.__redis_pubsub.subscribe(SorterConfig.TOPIC_STT_CARTON_AFTER_INSPECTION)
        self.__sub_value_tranfer()
        Logger().info("TRANFER READY")
    
    @Worker.employ
    def __sub_value_tranfer(self):
        while True:
            for message in self.__redis_pubsub.listen():
                if message['type'] == 'message':
                    self.__handle_tranfer(message["data"])

    def __handle_tranfer(self, message: str):
        if message.endswith(';'):
            result = self.__db_connection.get_final_result_carton(message)
            
            if result == HandleCartonConfig.OK:
                self.__PLC_controller.request_tranfer_ok()
                Logger().info(f"Qrcode: {message}, Result tranfer: {result}")
            else:   
                self.__PLC_controller.request_tranfer_ng()
                Logger().info(f"Qrcode: {message}, Result tranfer: {result}")

            time.sleep(TIME.TRANFER_SAMPLING_TIME_RESET)
            self.__PLC_controller.done_request_tranfer()
        else:
            Logger().error(f"QrCode incorect: {message}")
            

            
            



