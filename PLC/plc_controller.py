from config.constants import RegisterConfig, MarkemConfig, SorterConfig, HandlePalletConfig, DeviceConfig, DeviceConnectStatus, DWSConfig
from PLC.plc_interface import PLCSInterface
from utils.pattern import Singleton
from utils.threadpool import Worker
from db_redis import redis_cache
from config.settings import TIME
from config import CFG_MODBUS
from time import sleep
import numpy as np
import threading
from utils.logger import Logger
class PLCController(metaclass= Singleton):

    def __init__(self):
        """
        Initializes the connection parameters for the PLC station.

        Args:
            host: IP address of the PLC (default: "127.0.0.1")
            port: Modbus TCP port (default: 502)
            timeout: Timeout for Modbus operations (default: 1 second)
            unit: Modbus slave ID (default: 1)
        """
        self.__map_plc = RegisterConfig.REGISTER_CONFIG
        self.__redis_cache = redis_cache
        self.__PLC_interface = PLCSInterface(**CFG_MODBUS)



        background_thread = threading.Thread(target=self.__check_trigger)
        background_thread.daemon = True
        background_thread.start()


        self.__redis_pubsub = redis_cache.get_connection().pubsub()
        self.__redis_pubsub.subscribe(DeviceConnectStatus.TOPIC_CONNECTION_STATUS_MARKEM)
        self.get_conmcection_status_markem()

    @Worker.employ
    def get_conmcection_status_markem(self) -> bool:
        while True:
            for message in self.__redis_pubsub.listen():
                if message['type'] == 'message':
                    self.conmcection_status_markem(message["data"])


    def conmcection_status_markem(self, message):
        if message == DeviceConnectStatus.CONNECTED:
            self.status_markem_connect()
        else:
            self.status_markem_disconnect()
    


    def trigger_print(self, topic: str, message: str):
        self.__redis_cache.publisher(topic=topic, message=message)      

    def update_status(self, group, topic, value):
        self.__redis_cache.hset(group, topic, value)
        
        if topic == DeviceConfig.STATUS_DOCK_A1 and value == DeviceConfig.DOCK_PROCESSING :
            data_pallet_A1 = self.__redis_cache.hget(
                HandlePalletConfig.PALLET_DATA_MANAGEMENT, 
                HandlePalletConfig.INPUT_PALLET_A1_DATA   
            )
            if data_pallet_A1:
                self.__redis_cache.append_to_list(
                    HandlePalletConfig.LIST_PALLET_RUNNING, 
                    data_pallet_A1
                )
                
                self.__redis_cache.hdel(
                    HandlePalletConfig.PALLET_DATA_MANAGEMENT, 
                    HandlePalletConfig.INPUT_PALLET_A1_DATA
                )
        elif topic == DeviceConfig.STATUS_DOCK_A2 and value == DeviceConfig.DOCK_PROCESSING  :
            data_pallet_A2 = self.__redis_cache.hget(
                HandlePalletConfig.PALLET_DATA_MANAGEMENT, 
                HandlePalletConfig.INPUT_PALLET_A2_DATA   
            )
            if data_pallet_A2:
                self.__redis_cache.append_to_list(
                    HandlePalletConfig.LIST_PALLET_RUNNING, 
                    data_pallet_A2
                )
                self.__redis_cache.hdel(
                    HandlePalletConfig.PALLET_DATA_MANAGEMENT, 
                    HandlePalletConfig.INPUT_PALLET_A2_DATA
                )

        if topic == DeviceConfig.MARKEM_PRINTER_RESULTS and value == DeviceConfig.PRINTED_WRONG:
            self.__redis_cache.publisher(MarkemConfig.TOPIC_MARKEM_PRINTER_RESULTS, MarkemConfig.MESSAGE_PRINTED_WRONG)
            Logger().info("Error barcode don't read")


    def process_positions(self, data, data_reg_now):
        positions = np.where(data)[0]
        qrcode_plc_read = []
        qrcode_changed = False  # Cờ theo dõi sự thay đổi QR code

        for register in positions:
            if register in self.__map_plc:
                # Xử lý các giá trị trạng thái dựa trên dữ liệu trong map_plc
                status_list = self.__map_plc[register]
                if 0 <= data_reg_now[register] < len(status_list) - 1:
                    status = status_list[data_reg_now[register] + 1]  # Tìm trạng thái tương ứng
                    self.update_status(DeviceConfig.STATUS_ALL_DEVICES, self.__map_plc[register][0], status)
                else:
                    pass


            if register == 19:
                # data_reg_now[register] is <class 'numpy.int64'> so convert to int
                self.update_status(HandlePalletConfig.NUMBER_CARTON_OF_PALLET, HandlePalletConfig.QUANTITY_FROM_PLC, int(data_reg_now[register]))
            
            if register == 24:
                self.trigger_print(DWSConfig.TOPIC_TOPIC_ERROR_NO_WEIGHT, DWSConfig.CARTON_NO_WEIGHT)
            
            if register == 36:
                self.trigger_print(MarkemConfig.TOPIC_NOTIFY_SEND_DATA_PRINT, MarkemConfig.MESSAGE_NOTIFY_PRINT)
            
            if 42 <= register <= 91:
                
                qrcode_plc_read.extend([chr(int(data_reg_now[i])) for i in range(42, 92)])
                qrcode_changed = True  

        # Gọi trigger_print một lần nếu đã có sự thay đổi QR code
        if qrcode_changed:
            # TODO: decode 16bit for 1 character
            decoded_qrcode = ''.join(qrcode_plc_read)
            if ';' in decoded_qrcode:
                decoded_qrcode = decoded_qrcode.split(';', 1)[0] + ';'
            self.trigger_print(SorterConfig.TOPIC_STT_CARTON_AFTER_INSPECTION, decoded_qrcode)


            #TODO: decode 16bit for 2 character
            # for register in range(42, 93):
            #     first_char = (data_reg_now[register] >> 8) & 0xFF
            #     second_char = data_reg_now[register] & 0xFF
            #     qrcode_plc_read.append(chr(first_char))
            #     qrcode_plc_read.append(chr(second_char))
    
            # decoded_qrcode = ''.join(qrcode_plc_read)
            # print(decoded_qrcode)
                

    # @Worker.employ
    def __check_trigger(self):
        Logger().info("START CHECK PLC")
        data_reg_last = np.array([None])
        data_reg_now = np.array([None])
        while True:
            data_reg_now = np.array(self.__PLC_interface.read_data(num_register=100))

            # print(data_reg_now[24])
            # print(data_reg_now[29])

            try:
                if np.any(data_reg_now == None):
                    continue
                else:
                    if np.any(data_reg_last == None):
                        # Khởi tạo mảng cùng kích thước với data_reg_now mang giá trị -1
                        data_reg_last = np.full_like(data_reg_now, -1)
                        # data_reg_last = np.ones_like(data_reg_now)
                        # Khởi tạo giá trị thanh ghi 36 bằng với giá trị hiện tại
                        data_reg_last[36] = data_reg_now [36]
                        data_reg_last[42:92] = data_reg_now[42:92]
                    else:
                        # Compare with the previous read and process any changes
                        changed_positions = data_reg_last != data_reg_now
                        self.process_positions(changed_positions, data_reg_now)
                        data_reg_last = data_reg_now
            except Exception as e:
                Logger().error(f"Check trigger error: {e}")

            sleep(TIME.PLC_SAMPLING_TIME)


    def send_info_pallet_A1(self, response: dict):
        self.__PLC_interface.write_data(address= 0, value= [int(response["layer_pallet"]), 
                                        int(response["standard_height"]),
                                        int(response["layer_pallet"]),
                                        int(response["layer_pallet"]),
                                        int(response["carton_pallet_qty"])
                                        ])
        self.__PLC_interface.write_data(address= 38, value= [int(response["standard_length"]), 
                                            int(response["standard_width"])
                                            ])

    def update_actual_carton_pallet(self, actual_carton_pallet: str):
        pallet_processed = self.__redis_cache.hget(
                DeviceConfig.STATUS_ALL_DEVICES, 
                HandlePalletConfig.PALLET_PROCESSED   
            )

        if pallet_processed == HandlePalletConfig.PALLET_DOCK_A1:
            self.__PLC_interface.write_data(address= 4, value= [int(actual_carton_pallet)])
        elif pallet_processed == HandlePalletConfig.PALLET_DOCK_A2:
            self.__PLC_interface.write_data(address= 9, value= [int(actual_carton_pallet)])
                                        

    def send_info_pallet_A2(self, response: dict):
        self.__PLC_interface.write_data(address= 5, value= [int(response["layer_pallet"]), 
                                        int(response["standard_height"]),
                                        int(response["layer_pallet"]),
                                        int(response["layer_pallet"]),
                                        int(response["carton_pallet_qty"])
                                        ])
        self.__PLC_interface.write_data(address= 40, value= [int(response["standard_length"]), 
                                        int(response["standard_width"])
                                        ])
    

    #LINE curtain
    def request_open_line_curtain(self, area: str):
        if area == "A":
            self.__PLC_interface.write_data(address= 10, value= [1])
        elif area == "O":
            self.__PLC_interface.write_data(address= 13, value= [1])

    def request_close_line_curtain(self, area: str):
        if area == "A":
            self.__PLC_interface.write_data(address= 11, value= [1])
        elif area == "O":
            self.__PLC_interface.write_data(address= 14, value= [1])

    def reset_request_open_line_curtain(self, area: str):
        if area == "A":
            self.__PLC_interface.write_data(address= 10, value= [0])
        elif area == "O":
            self.__PLC_interface.write_data(address= 13, value= [0])

    def reset_request_close_line_curtain(self, area: str):
        if area == "A":
            self.__PLC_interface.write_data(address= 11, value= [0])
        elif area == "O":
            self.__PLC_interface.write_data(address= 14, value= [0])
    
    def reset_all_request_line_curtain(self, area: str):
        if area == "A":
            self.__PLC_interface.write_data(address= 10, value= [0, 0])
        elif area == "O":
            self.__PLC_interface.write_data(address= 13, value= [0, 0])


    # Tranfer
    def request_tranfer_ng(self):
        self.__PLC_interface.write_data(address= 35, value= [0])
    
    def request_tranfer_ok(self):
        self.__PLC_interface.write_data(address= 35, value= [1])
    
    def done_request_tranfer(self):
        self.__PLC_interface.write_data(address= 21, value= [1])

    # MARKEM
    def status_markem_disconnect(self):
        self.__PLC_interface.write_data(address= 25, value= [0])

    def status_markem_connect(self):
        self.__PLC_interface.write_data(address= 25, value= [1])


    # DWS
    def status_DWS_connect(self):
        self.__PLC_interface.write_data(address= 22, value= [1])

    def status_DWS_disconnect_scale(self):
        self.__PLC_interface.write_data(address= 22, value= [2])

    def notify_error_no_weight(self):
        self.__PLC_interface.write_data(address= 29, value= [1])
        
    def reset_error_no_weight(self):
        self.__PLC_interface.write_data(address= 29, value= [0])
        self.__PLC_interface.write_data(address= 24, value= [0])


    # AGV
    def AGV_status_is_in_lifting_up(self):
        self.__PLC_interface.write_data(address= 93, value= [2])

    def AGV_status_is_out_lifting_up(self):
        self.__PLC_interface.write_data(address= 93, value= [1])

    def AGV_status_is_in_lifting_down(self):
        self.__PLC_interface.write_data(address= 94, value= [2])

    def AGV_status_is_out_lifting_down(self):
        self.__PLC_interface.write_data(address= 94, value= [1])


    # Button create mission AGV
    def set_status_light_button(self, mission_name: str):
        if mission_name == "MISSION_M1":
            self.__PLC_interface.write_data(address= 30, value= [2])
        elif mission_name == "MISSION_M2":
            self.__PLC_interface.write_data(address= 31, value= [2])
        elif mission_name == "MISSION_M3":
            self.__PLC_interface.write_data(address= 32, value= [2])

    def reset_status_light_button(self, mission_name: str):
        if mission_name == "MISSION_M1":
            self.__PLC_interface.write_data(address= 30, value= [3])
        elif mission_name == "MISSION_M2":
            self.__PLC_interface.write_data(address= 31, value= [3])
        elif mission_name == "MISSION_M3":
            self.__PLC_interface.write_data(address= 32, value= [3])