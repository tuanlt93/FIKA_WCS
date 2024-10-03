from config.constants import HandlePalletConfig, HandleCartonConfig, MarkemConfig, STATUS_PALLET_CARTON, ERROR_DWS, SETTING_SYSTEM
from apis.response_format import ResponseFomat
from utils.vntime import VnTimestamp, VnDateTime
from utils.pattern import Custom_Enum
from apis.api_base import ApiBase
from apis.DAL.func_pda import CallApiBackEnd
from utils.logger import Logger
from db_redis import redis_cache
from PLC import PLC_controller
from flask import request
import json
import random


class DWSHeartBeat(ApiBase):
    """
        Start pallet carton
    """
    urls = ("/dws/heartbeat",)

    def __init__(self) -> None:
        self.__logger = Logger()
        self.__PLC_controller = PLC_controller
        return super().__init__()

    @ApiBase.exception_error
    def post(self):
        datas = self.jsonParser([], [])
        if datas:
            # print(datas)
            self.__PLC_controller.status_DWS_connect()
            return ApiBase.createResponseMessage({}, "OKE")
        return ApiBase.createNotImplement()
    



class DWSResult(ApiBase):
    """
        Thông tin sau khi thùng carton đi qua DWS
    """
    urls = ("/dws/result",)

    def __init__(self) -> None:
        self.__call_backend = CallApiBackEnd()
        self.__logger = Logger()
        self.__PLC_controller = PLC_controller
        self.__redis_cache = redis_cache

        return super().__init__()

    @ApiBase.exception_error
    def post(self):
        """
        DWS_RESULT = [
            "height" , "width" , "length" , "weight" , 
            "status" , "link"
        ]
        """
        args = ResponseFomat.DWS_RESULT
        DWS_result = self.jsonParser(args, args)
        print(DWS_result)
        if DWS_result["weight"] == -1:
            self.__PLC_controller.notify_error_two_cartons()
            print("HAI THUNG")
            return ApiBase.createNotImplement()
        
        
        # Lấy số lượng từ đếm thùng từ PLC
        current_quantity_PLC = self.__redis_cache.hget(
            HandlePalletConfig.NUMBER_CARTON_OF_PALLET, 
            HandlePalletConfig.QUANTITY_FROM_PLC
        )

        # Kiểm tra điều kiện để kết thúc pallet
        if int(current_quantity_PLC) == 0 and (int(quantity_carton_DWS) + 1) >= int(data_pallet_carton_input["carton_pallet_qty"]):
            print("DONE PALLET")
            self.__call_backend.UpdateSttPalletCarton(data_pallet_carton_input["_id"])


        # Bắt đầu pallet khacs
        data_pallet_carton_input = self.__redis_cache.get_first_element(HandlePalletConfig.LIST_PALLET_RUNNING)
        data_pallet_carton_input = json.loads(data_pallet_carton_input)

        if DWS_result:
            # update số lượng carton dws đếm được
            quantity_carton_DWS = self.__redis_cache.hget(
                HandlePalletConfig.NUMBER_CARTON_OF_PALLET, 
                HandlePalletConfig.QUANTITY_FROM_DWS
            )

            # Kiểm tra điều kiện để bắt đầu pallet
            if (int(quantity_carton_DWS) + 1) == 1:
                self.__call_backend.startPalletCarton()


            self.__redis_cache.hset(
                HandlePalletConfig.NUMBER_CARTON_OF_PALLET, 
                HandlePalletConfig.QUANTITY_FROM_DWS,
                int(quantity_carton_DWS) + 1
            )

            check_carton_print, check_carton_backend = self.__check_range(
                DWS_result["length"],
                DWS_result["width"],
                DWS_result["height"],
                DWS_result["weight"] * 1000,
                DWS_result["status"],
                float(data_pallet_carton_input["standard_length"]),
                float(data_pallet_carton_input["standard_width"]),
                float(data_pallet_carton_input["standard_height"]),
                float(data_pallet_carton_input["standard_weight"]),
                int(quantity_carton_DWS) + 1
            )
            
            # Tạo data cho máy in
            data_print_lable = {
                "material_code" : data_pallet_carton_input["material_code"],
                "vendor_batch"  : data_pallet_carton_input["vendor_batch"],
                "sap_batch"     : data_pallet_carton_input["sap_batch"],
                "expire_date"   : data_pallet_carton_input["expiry_date"],
                "quantity"      : data_pallet_carton_input["carton_pallet_qty"],
                "carton_id"     : (
                    data_pallet_carton_input["carton_pallet_code"] + "," +
                    str(int(quantity_carton_DWS) + 1) + "," +
                    check_carton_print  +";"
                )   
            }
            self.__redis_cache.append_to_list(MarkemConfig.DATA_CARTON_LABLE_PRINT, data_print_lable)



            """
                Tao moi 1 luong chay qc carton
                {
                    "carton_code": "string",
                    "carton_pallet_id": "string",
                    "dws_result": "string",
                    "actual_length": 0,
                    "actual_width": 0,
                    "actual_height": 0,
                    "actual_weight": 0,
                    "actual_item_carton": 0,
                    "link": "string",
                    "description": "string"
                }
                ---> OKE
            """

            data_creat_carton = {
                "carton_code": data_print_lable["carton_id"],
                "carton_pallet_id": data_pallet_carton_input["_id"],
                "dws_result": check_carton_backend,
                "actual_length": DWS_result["length"],
                "actual_width": DWS_result["width"],
                "actual_height": DWS_result["height"],
                "actual_weight": DWS_result["weight"] * 1000,
                "actual_item_carton": data_pallet_carton_input["standard_item_carton"],
                "link": DWS_result["link"],
                "description": ""
            }
            response = self.__call_backend.createCarton(data_creat_carton)
            # print(response)
            
                    

            return ApiBase.createResponseMessage({}, "OKE")
        return ApiBase.createNotImplement()
    




    def __check_range(self, height, length, width, weight, status, 
                    standard_height, standard_length, standard_width, standard_weight, number_carton):
        
        data_system_json = self.__redis_cache.get(SETTING_SYSTEM.TOPIC_SETTING_SYSTEM)
        data_system = json.loads(data_system_json)
        
            
        lower_height = standard_height - data_system[SETTING_SYSTEM.DWS_SIZE]
        upper_height = standard_height + data_system[SETTING_SYSTEM.DWS_SIZE]

        lower_length = standard_length - data_system[SETTING_SYSTEM.DWS_SIZE]
        upper_length = standard_length + data_system[SETTING_SYSTEM.DWS_SIZE]

        lower_width = standard_width - data_system[SETTING_SYSTEM.DWS_SIZE]
        upper_width = standard_width + data_system[SETTING_SYSTEM.DWS_SIZE]

        lower_weight = standard_weight - data_system[SETTING_SYSTEM.DWS_WEIGHT]
        upper_weight = standard_weight + data_system[SETTING_SYSTEM.DWS_WEIGHT]

        interval = data_system[SETTING_SYSTEM.INTERVAL]


        if number_carton == 1 or random.uniform(0, 100) <= interval:
            return "1", HandleCartonConfig.OK_CHECK
        else:
            if (lower_height <= height <= upper_height and
                lower_length <= length <= upper_length and
                lower_width <= width <= upper_width and
                status == "OK"
                ):
                    
                if weight > upper_weight:
                    return "1", ERROR_DWS.OVER_WEIGHT
                elif weight < lower_weight:
                    return "1", ERROR_DWS.UNDER_WEIGHT
                else:
                    return "0", "OK"
                
            else:
                if lower_weight <= weight <= upper_weight:
                    return "1", ERROR_DWS.WRONG_SIZE
                elif weight > upper_weight:
                    return "1", ERROR_DWS.WRONG_SIZE_OVER_WEIGHT
                elif weight < lower_weight:
                    return "1", ERROR_DWS.WRONG_SIZE_UNDER_WEIGHT

                return "1", "NG"