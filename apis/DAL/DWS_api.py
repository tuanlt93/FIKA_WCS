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
import time


time_last = time.time() 
class DWSHeartBeat(ApiBase):
    """
        Start pallet carton
    """
    urls = ("/dws/heartbeat",)

    def __init__(self) -> None:
        self.__PLC_controller = PLC_controller
        super().__init__()

    @ApiBase.exception_error
    def post(self):
        global time_last 
        datas = self.jsonParser([], [])
        # print(datas)
        if datas:
            self.__PLC_controller.status_DWS_connect()  
            time_now = time.time()  
            time_difference = time_now - time_last
            if time_difference > 10:
                Logger().error(f"DWS error connect: Time since last heartbeat is {time_difference:.2f} seconds")   
            time_last = time_now  
            return ApiBase.createResponseMessage({}, "OKE")
        return ApiBase.createNotImplement()


class DWSResult(ApiBase):
    """
        Thông tin sau khi thùng carton đi qua DWS
    """
    urls = ("/dws/result",)

    def __init__(self) -> None:
        self.__call_backend = CallApiBackEnd()
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
        # print(DWS_result)



         # Lấy số lượng từ đếm thùng từ PLC và DWS chỉ một lần
        quantity_data = self.__redis_cache.hgetall(
            HandlePalletConfig.NUMBER_CARTON_OF_PALLET, 
        )
        current_quantity_PLC = int(quantity_data[HandlePalletConfig.QUANTITY_FROM_PLC])
        quantity_carton_DWS = int(quantity_data[HandlePalletConfig.QUANTITY_FROM_DWS])

       

        # LẤY DỮ LIỆU PALLET ĐANG CHẠY
        data_pallet_carton_input = self.__redis_cache.get_first_element(HandlePalletConfig.LIST_PALLET_RUNNING)
        data_pallet_carton_input = json.loads(data_pallet_carton_input)

       


        # Kiểm tra điều kiện để kết thúc pallet
        if (
            (current_quantity_PLC in HandlePalletConfig.LIST_NUMBER_CARTON_START_NEW_PALLET) and 
            (quantity_carton_DWS) >= int(data_pallet_carton_input["carton_pallet_qty"])
        ):
            # Kết thúc Pallet 
            self.__call_backend.UpdateSttPalletCarton(data_pallet_carton_input["_id"])

            # LẤY DỮ LIỆU PALLET MỚI
            data_pallet_carton_input = self.__redis_cache.get_first_element(HandlePalletConfig.LIST_PALLET_RUNNING)
            data_pallet_carton_input = json.loads(data_pallet_carton_input)

            # Đưa giá trị đếm DWS về 0
            quantity_carton_DWS = 0

            # Xóa data in pallet cũ
            self.__redis_cache.delete(MarkemConfig.DATA_CARTON_LABLE_PRINT)
            Logger().info("Done Pallet")


        Logger().info(f"Result DWS: {DWS_result}, number: {quantity_carton_DWS + 1}")


         # Lỗi cân không được hoặc thùng cặp kè (khi khối lượng một thùng vượt quá 170% khối lượng standard)
        if DWS_result["weight"] == -1 or (DWS_result["weight"] * 1000) > (int(data_pallet_carton_input["standard_weight"]) * 1.7):
            self.__PLC_controller.notify_error_no_weight()
            Logger().info("LOI CAN DWS HOAC 2 THUNG VAO CAN")
            return ApiBase.createNotImplement()


        # Kiểm tra điều kiện để bắt đầu pallet
        if (quantity_carton_DWS + 1) == 1:
            self.__call_backend.startPalletCarton()

        check_carton_print, check_carton_backend = self.__check_range(
            round(DWS_result["length"]),
            round(DWS_result["width"]),
            round(DWS_result["height"]),
            DWS_result["weight"] * 1000,
            DWS_result["status"],
            int(data_pallet_carton_input["standard_length"]),
            int(data_pallet_carton_input["standard_width"]),
            int(data_pallet_carton_input["standard_height"]),
            int(data_pallet_carton_input["standard_weight"]),
            (quantity_carton_DWS + 1)
        )
        

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
            "carton_code": data_pallet_carton_input["carton_pallet_code"] + "," +
                str(quantity_carton_DWS + 1) + "," +
                check_carton_print  +";",
            "carton_pallet_id": data_pallet_carton_input["_id"],
            "dws_result": check_carton_backend,
            "actual_length": round(DWS_result["length"]),
            "actual_width": round(DWS_result["width"]),
            "actual_height": round(DWS_result["height"]),
            "actual_weight": DWS_result["weight"] * 1000,
            "actual_item_carton": data_pallet_carton_input["standard_item_carton"],
            "link": DWS_result["link"],
            "description": ""
        }
        response = self.__call_backend.createCarton(data_creat_carton)

        # Tạo data cho máy in
        data_print_lable = {
            "material_code" : data_pallet_carton_input["material_code"],
            "material_name" : data_pallet_carton_input["material_name"],
            "vendor_batch"  : data_pallet_carton_input["vendor_batch"],
            "sap_batch"     : data_pallet_carton_input["sap_batch"],
            "expire_date"   : data_pallet_carton_input["expiry_date"],
            "quantity"      : data_pallet_carton_input["standard_item_carton"],
            "carton_id"     : response['metaData']['carton_code'] + ";"
        }
        self.__redis_cache.append_to_list(MarkemConfig.DATA_CARTON_LABLE_PRINT, json.dumps(data_print_lable))

        # Update số lượng carton DWS đếm được
        self.__redis_cache.hset(
            HandlePalletConfig.NUMBER_CARTON_OF_PALLET, 
            HandlePalletConfig.QUANTITY_FROM_DWS,
            (quantity_carton_DWS + 1)
        )

        return ApiBase.createResponseMessage({}, "OKE")

    

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