from config.constants import DWSConfig, DeviceConfig
from db_redis import redis_cache
from PLC import PLC_controller
from utils.threadpool import Worker
from utils.logger import Logger
import time

class HandleDWS():
    def __init__(self) -> None:
        super().__init__()
        self.__PLC_controller = PLC_controller
        self.__redis_cache = redis_cache
        self.__redis_pubsub = redis_cache.get_connection().pubsub()
        self.__redis_pubsub.subscribe(DWSConfig.TOPIC_TOPIC_ERROR_NO_WEIGHT)
        self.__sub_request()
    
    @Worker.employ
    def __sub_request(self):
        Logger().info("START CHECK DWS")
        while True:
            for message in self.__redis_pubsub.listen():
                if message['type'] == 'message':
                    self.handle(message["data"])

    def handle(self, message):
        if message == DWSConfig.CARTON_NO_WEIGHT:
            Logger().info("Reset error no weight DWS")
            while True:
                try:
                    notify_reset_no_weight = self.__redis_cache.hget(
                        DeviceConfig.STATUS_ALL_DEVICES,
                        DeviceConfig.STATUS_NOTIFY_RETURN_CARTONS
                    )
                    if notify_reset_no_weight == DeviceConfig.ACEPTED:
                        self.__PLC_controller.reset_error_no_weight()
                    elif notify_reset_no_weight == DeviceConfig.WAIT_ACCEPT:
                        break
                except Exception as e:
                    Logger().info(f"Error reset no weight DWS: {e}" )
                
                time.sleep(5)
            



