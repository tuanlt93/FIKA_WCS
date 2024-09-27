from apis.api_base import ApiBase
from apis.DAL.func_pda import CallApiBackEnd

# from .handle import Manage_Queue
import json
from flask import request

from utils.logger import Logger
from utils.vntime import VnTimestamp, VnDateTime
from config.constants import HandleCartonConfig, HandlePalletConfig, TOPIC_WCS_PUBSUB, DeviceConfig
from apis.response_format import ResponseFomat, BE_TypeCartonError
from db_redis import redis_cache




"""
    DAL giao tiếp với backend
"""
class PDA_Input(ApiBase):
    """
        - Tạo mới khi nhập màn hình input trong pda: 
        msg = {
            "material_code": "204104343",
            "material_name": "THUỐC CẢM CÚM",
            "vendor_batch": "BXJKH91",
            "sap_batch": "F-BXJKH91",
            "expiry_date": "1767139200000",
            "layer_pallet": 5,
            "carton_pallet_qty": 50,
            "standard_min": 100,
            "standard_medium": 240,
            "standard_max": 300,
            "standard_weight": 1500,
            "standard_item_carton": 100
        }

        - Data set queue redis: 
        datas = {
            "material_code": "21192776",
            "material_name": "Thuốc cảm",
            "vendor_batch": "FGHJK",
            "sap_batch": "F-FGHJK",
            "expiry_date": "09/07/2025",
            "layer_pallet": 4,
            "carton_pallet_qty": 30,
            "standard_min": 200,
            "standard_medium": 300,
            "standard_max": 400,
            "standard_weight": 10,
            "standard_item_carton": 100,
            "stt_carton": 0,
            "status": pending,
            "_id" = "66cb6949cb5be5b2b05b7ff0
        }

        Pallet ID: 372761,XZMN42,20240418,10,50 (Material Code, vendor_batch, Số thứ tự của Pallet này trong số các Pallet thuộc Material Code 372761 trong ngày, carton_pallet_qty)

        ---> OKE
    """

    urls = ("/pda/input",)

    def __init__(self) -> None:
        self.__logger = Logger()
        self.__redis_cache = redis_cache
        return super().__init__()
    
    # @ApiBase.exception_error
    def post(self):
        args = ResponseFomat.API_PDA_INPUT
        datas = self.jsonParser(args, args)
        datas_json = json.dumps(datas)
        self.__redis_cache.hset(
            HandlePalletConfig.PALLET_DATA_MANAGEMENT,
            HandlePalletConfig.PALLET_INPUT_DATA,
            datas_json
        )
        return ApiBase.createResponseMessage({}, "Creat pallet input successful")



    # @ApiBase.exception_error
    # def post(self):
    #     args = ResponseFomat.API_PDA_INPUT
    #     datas = self.jsonParser(args, args)
    #     response = self.__create_pallet(datas)
    #     print(response)
    #     if response:
    #         if response.status_code != 201:
    #             return ApiBase.createResponseMessage({}, response['message'], response['statusCode'], response['statusCode'])
    #         else:
    #             response = response.json()
    #             datas["stt_carton"] = response['metaData']["stt_carton"]
    #             datas["status"] = response['metaData']["status"]
    #             datas["_id"] = response['metaData']["_id"]


    #             # Lưu data pallet có được vào redis
    #             self.__redis_cache.append_to_list(topic= HandlePalletConfig.LIST_PALLET_INPUT_DATA, item= datas) 


    #             return ApiBase.createResponseMessage({}, response['msg'])
    #     return ApiBase.createNotImplement()







class ConfirmQtyPalletCarton(ApiBase):
    """
        - Màn hình quantity of cartons/pallet 
        (màn hình hiển thị khi số lượng carton đi qua cảm biến khác với input)
        - Data get first queue redis: 
        datas = {
            "material_code": "21192776",
            "material_name": "Thuốc cảm",
            "vendor_batch": "FGHJK",
            "sap_batch": "F-FGHJK",
            "expiry_date": "09/07/2025",
            "layer_pallet": 4,
            "carton_pallet_qty": 30,
            "standard_min": 200,
            "standard_medium": 300,
            "standard_max": 400,
            "standard_weight": 10,
            "standard_item_carton": 100,
            "stt_carton": 0,
            "status": pending,
            "_id" = "66cb6949cb5be5b2b05b7ff0
        }

        - Response get info pallet
        response = {
            "msg": "Ok",
            "metaData": {
                "_id": "66b65a95df18671ff7f73c3c",
                "material_id": {
                    "_id": "666688eafe323bd516c08a64",
                    "material_code": "304013045",
                    "material_name": "Thuốc dạ dày"
                },
                "carton_pallet_code": "304013045,BXJKH91,20240530,6,50",
                "vendor_batch": "BXJKH91",
                "sap_batch": "F-BXJKH91",
                "expiry_date": "46022",
                "layer_pallet": 5,
                "carton_pallet_qty": 50,
                "standard_max": 300,
                "standard_medium": 240,
                "standard_min": 200,
                "standard_weight": 1500,
                "standard_item_carton": 100,
                "stt_carton": 39,
                "status": "pending",
                "createdAt": "2024-08-09T18:06:13.114Z",
                "updatedAt": "2024-08-09T18:06:13.114Z",
                "__v": 0
            }
        }


        ---> OKE
    """
    urls = ("/pda/confirm_qty",)

    def __init__(self) -> None:
        self.__api_backend = CallApiBackEnd()
        self.__confirm_carton_state = self.__api_backend.confirmCartonState
        self.__get_carton_pallet = self.__api_backend.palletInfo

        self.__redis_cache = redis_cache
        self.__logger = Logger()
        return super().__init__()

    @ApiBase.exception_error
    def get(self):

        status_pallet_running = self.__redis_cache.hget(DeviceConfig.STATUS_ALL_DEVICES, HandlePalletConfig.STATUS_PALLET_RUNNING)
        if status_pallet_running != HandlePalletConfig.ENOUGH_CARTONS:
            datas = self.jsonParser([], [])


            # Lấy data pallet đang chạy, tùy vào pallet vị trí dock A1, dock A2
            data_pallet_run = self.__redis_cache.get_first_element(HandlePalletConfig.LIST_PALLET_RUNNING)
            info_carton_run = json.loads(data_pallet_run)


            _id = info_carton_run["_id"]
            if not _id:
                return ApiBase.createNotImplement() 
            response = self.__get_carton_pallet(_id)
            print(response.text)

            if response:
                print("------------", response.status_code)
                if response.status_code != 200:
                    return ApiBase.createResponseMessage({}, response['message'], response['statusCode'], response['statusCode'])
                else:
                    response = response.json()
                    datas = response['metaData']
                    datas['material_code'] = datas['material_id']['material_code']
                    datas['material_name'] = datas['material_id']['material_name']
                    datas['material_id'] = datas['material_id']['_id']
                    datas['qty_sensor'] = datas["stt_carton"]
                    return ApiBase.createResponseMessage(datas, response['msg'])
        return ApiBase.createNotImplement() 



    @ApiBase.exception_error
    def post(self):
        args = ResponseFomat.API_PDA_CONFIRM_QTY
        datas = self.jsonParser(args, args)
        data = {
            "carton_pallet_code" : datas['pallet_code'],
            "carton_pallet_qty" : datas['actual_carton_pallet']
        }

        print(data)

        response = self.__confirm_carton_state(data)
        if response.status_code != 201:
            response = response.json()
            return ApiBase.createResponseMessage({}, response['message'], response['statusCode'], response['statusCode'])
        else:
            response = response.json()
            return ApiBase.createResponseMessage({}, response['msg'])
        




class GetCartonStateInputError(ApiBase):
    """
        màn hình inspection và correction -> OKE
    """
    urls = ("/pda/carton_error/info",)

    def __init__(self) -> None:
        self.__api_backend = CallApiBackEnd()
        self.__get_input_insection_or_correction = self.__api_backend.getInputInsectionOrCorrection
        self.__logger = Logger()
        return super().__init__()

    @ApiBase.exception_error
    def get(self):
        args = ResponseFomat.API_CARTON_STATE_INPUT_ERROR
        datas = self.jsonParser(args, args)
        response = self.__get_input_insection_or_correction(datas)
        if response.status_code != 200:
            response = response.json()
            return ApiBase.createResponseMessage({}, response['message'], response['statusCode'], response['statusCode'])
        else:
            response = response.json()
            return ApiBase.createResponseMessage(response["metaData"], response['msg'])
        



class CreateInspection(ApiBase):
    """
        Tạo inspection
    """
    urls = ("/pda/carton_error/create/inspection",)

    def __init__(self) -> None:

        self.__api_backend = CallApiBackEnd()

        self.__input_insection_or_correction = self.__api_backend.inputInsectionOrCorrection
        self.__info_carton_state = self.__api_backend.cartonInfo
        self.__update_carton_state = self.__api_backend.updateState
        self.__update_visa = self.__api_backend.updateVisa
        self.__update_carton_qty = self.__api_backend.updateCartonQty
        self.__final_carton_state = self.__api_backend.finalCartonState
        self.__find_material_by_carton_state = self.__api_backend.findMaterialByCartonState
        self.__pda_history = self.__api_backend.pdaHistory

        self.__redis_cache = redis_cache
        self.manage_queue = Manage_Queue()
        self.__logger = Logger()
        return super().__init__()

    # @ApiBase.exception_error
    def post(self):
        args = ResponseFomat.API_CREATE_INSPECTION
        datas = self.jsonParser(args, args)
        datas["type_error"] = BE_TypeCartonError.INSPECTION

        self.__input_insection_or_correction(datas)

        if request.headers.get('Authorization') == None:
            return ApiBase.createResponseMessage({}, "Token is required", 401, 401)
        
        response = self.__pda_history( datas, request.headers.get('Authorization'))

        if response.status_code != 201:
            response = response.json()
            return ApiBase.createResponseMessage({}, response['message'], response['statusCode'], response['statusCode'])
        else:
            response = response.json()
            carton_state = self.__info_carton_state(datas['carton_state_id'])
            carton_state_data = carton_state.json()
            if carton_state.status_code != 200:
                return ApiBase.createResponseMessage({}, carton_state_data['message'])
            

            self.__update_carton_state(datas['carton_state_id'], {
                "actual_item_carton" : datas['actual_item_carton']
            })


            self.updateVisa(datas, carton_state_data)
            self.checkStatus(datas, carton_state_data)
            return ApiBase.createResponseMessage(response["metaData"], response['msg'])
        

    def updateVisa(self, datas, carton_state):
        carton_pallet_id = carton_state['metaData']['carton_pallet_id']['_id']
        out_data = {
            "visa" : datas["visa"]
        }
        self.__update_visa(carton_pallet_id, out_data)
    

    def checkStatus(self, datas, carton_state):
        """
            Kiểm tra trạng thái DWS và inspection
        """
        carton_state_id = datas['carton_state_id']
        if "final_result" not in carton_state['metaData']:
            carton_state['metaData']["final_result"] = None

        final_result = carton_state['metaData']['final_result']

        if (
            final_result != HandleCartonConfig.OK and datas['result'] != HandleCartonConfig.OK
        ) or (
            final_result == HandleCartonConfig.OK and datas['result'] == HandleCartonConfig.OK
        ):
            self.__update_carton_state(carton_state_id, {
                "inspection_result" : datas['result']
            })


        elif (final_result == HandleCartonConfig.OK and datas['result'] != HandleCartonConfig.OK):
            data = {
                "final_qty" : -1,
                "final_ok_qty" : -1
            }
            data_material = self.__find_material_by_carton_state(carton_state_id)
            data_material = data_material.json()
            material_id = data_material['metaData']['_id']
            self.__update_carton_qty(material_id, data)
            self.__update_carton_state(carton_state_id, {
                "inspection_result" : datas['result'],
                "$unset": { "final_result": "" }
            })


        elif (final_result != HandleCartonConfig.OK and datas['result'] == HandleCartonConfig.OK):
            self.__final_carton_state(carton_state_id, {
                "inspection_result" : datas['result']
            })


        # lưu vào redis
    #     datas["inspection_result"] = datas['result']
    #     data_redis = self.convert_carton_state(carton_state)
    #     # print("data_redis :", data_redis)
    #     self.__redis_cache.set_dict(TOPIC_REDIS.CARTON_INFO + data_redis['carton_code'], data_redis)
    #     self.manage_queue.AddSort_2(data_redis['carton_code'])
            


    # def convert_carton_state(self, datas):
    #     carton_state_info = datas['metaData']
    #     carton_state_info['material_code'] = carton_state_info['carton_pallet_id']['material_id']['material_code']
    #     carton_state_info['material_name'] = carton_state_info['carton_pallet_id']['material_id']['material_name']
    #     carton_state_info['material_id'] = carton_state_info['carton_pallet_id']['material_id']['_id']
    #     carton_state_info['carton_pallet_id'] = carton_state_info['carton_pallet_id']['_id']
    #     for carton_key in carton_state_info:
    #         if carton_state_info[carton_key] == None:
    #             carton_state_info[carton_key] = ""
    #     return carton_state_info  




class CreateCorrection(ApiBase):
    """
        Tạo correction
    """
    urls = ("/pda/carton_error/create/correction",)

    def __init__(self) -> None:
        self.__api_backend = CallApiBackEnd()
        self.__input_nsection_or_correction = self.__api_backend.inputInsectionOrCorrection
        self.__update_carton_state = self.__api_backend.updateState
        self.__final_carton_state = self.__api_backend.finalCartonState
        self.__update_carton_qty = self.__api_backend.updateCartonQty
        self.__find_material_by_carton_state = self.__api_backend.findMaterialByCartonState
        self.__info_carton_state = self.__api_backend.cartonInfo
        self.__pda_history = self.__api_backend.pdaHistory
        self.__logger = Logger()
        return super().__init__()

    @ApiBase.exception_error
    def post(self):
        args = ResponseFomat.API_CREATE_CORRECTION
        datas = self.jsonParser(args, args)
        # print(datas)
        datas["type_error"] = BE_TypeCartonError.CORRECTION
        self.__input_nsection_or_correction(datas)
        data_state = {
            "correction_result": datas['result'],
            "final_result" : datas['result']
        }
        if request.headers.get('Authorization') == None:
            return ApiBase.createResponseMessage({}, "Token is required", 401, 401)
        response = self.__pda_history( datas, request.headers.get('Authorization'))
        if response.status_code != 201:
            response = response.json()
            return ApiBase.createResponseMessage({}, response['message'], response['statusCode'], response['statusCode'])
        else:
            response = response.json()
            carton_state = self.__info_carton_state(datas['carton_state_id'])
            # self.__final_carton_state(datas['carton_state_id'], data_state)
            carton_state_data = carton_state.json()
            if carton_state.status_code != 200:
                return ApiBase.createResponseMessage({}, carton_state_data['message'])
            self.__update_carton_state(datas['carton_state_id'], {
                "actual_item_carton" : datas['actual_item_carton']
            })
            self.checkStatus(datas, carton_state_data)
            return ApiBase.createResponseMessage(response["metaData"], response['msg'])
        
    def checkStatus(self, datas, carton_state):
        """
            Kiểm tra trạng thái DWS và correction
        """
        try:
            carton_state_id = datas['carton_state_id']
            if "final_result" not in carton_state['metaData']:
                self.__final_carton_state(carton_state_id, {
                    "correction_result" : datas['result']
                })
                return None
            final_result = carton_state['metaData']['final_result']
            data_status = {
                "correction_result" : datas['result'],
                "final_result" : datas['result']
            }
            if (final_result == HandleCartonConfig.OK and datas['result'] != HandleCartonConfig.OK):
                data_qty = {
                    "final_ng_qty" : 1,
                    "final_ok_qty" : -1
                }
                self.updateDataBackend(data_qty, data_status, carton_state_id)
            elif (final_result != HandleCartonConfig.OK and datas['result'] == HandleCartonConfig.OK):
                data_qty = {
                    "final_ng_qty" : -1,
                    "final_ok_qty" : 1
                }
                self.updateDataBackend(data_qty, data_status, carton_state_id)
            return None
        except Exception as e:
            print(e)
        

    def updateDataBackend(self, data_qty, data_status, carton_state_id):
        data_material = self.__find_material_by_carton_state(carton_state_id)
        data_material = data_material.json()
        material_id = data_material['metaData']['_id']
        self.__update_carton_qty(material_id, data_qty)
        self.__update_carton_state(carton_state_id, data_status)











class PdaPrint(ApiBase):
    """
        Màn hình print
    """
    urls = ("/pda/print",)

    def __init__(self) -> None:
        self.__api_backend = CallApiBackEnd()
        self.__get_carton_code = self.__api_backend.getCartonStateCode
        self.__redis_cache = redis_cache
        self.__logger = Logger()
        return super().__init__()

    @ApiBase.exception_error
    def get(self):
        datas = self.jsonParser(["carton_code"], [])
        response = self.__get_carton_code(datas)
        if response:
            if response.status_code != 200:
                return ApiBase.createResponseMessage({}, response['message'], response['statusCode'], response['statusCode'])
            else:
                response = response.json()
                datas = response['metaData']
                datas['material_code'] = datas['carton_pallet_id']['material_id']['material_code']
                datas['material_name'] = datas['carton_pallet_id']['material_id']['material_name']
                datas['material_id'] = datas['carton_pallet_id']['material_id']['_id']
                datas['vendor_batch'] = datas['carton_pallet_id']['vendor_batch']
                datas['sap_batch'] = datas['carton_pallet_id']['sap_batch']
                datas['expiry_date'] = VnTimestamp.get_ddmmyyy_to_timestamp(datas['carton_pallet_id']['expiry_date'])
                datas['carton_pallet_id'] = datas['carton_pallet_id']['_id']
                return ApiBase.createResponseMessage(datas, response['msg'])
        return ApiBase.createNotImplement() 

    @ApiBase.exception_error
    def post(self):
        args = ResponseFomat.API_PRINT
        datas = self.jsonParser(args, args)
        




        #TODO: Gửi thông báo và data đến máy in datamax ---> Đổi lại dùng requests POST
        self.__redis_cache.publisher(TOPIC_WCS_PUBSUB.PRINTER_IN_PDA,  json.dumps(datas))






        return ApiBase.createResponseMessage({}, "Success")




class PdaPrintPresent(ApiBase):
    """
        Màn hình print carton trước đó
    """
    urls = ("/pda/print_present",)

    def __init__(self) -> None:

        self.__api_backend = CallApiBackEnd()
        self.__carton_printer = self.__api_backend.cartonPrinter
        self.__logger = Logger()
        return super().__init__()

    @ApiBase.exception_error
    def get(self):
        datas = self.jsonParser([], [])
        response = self.__carton_printer()
        if response:
            if response.status_code != 200:
                return ApiBase.createResponseMessage({}, response['message'], response['statusCode'], response['statusCode'])
            else:
                response = response.json()
                datas = response['metaData']
                datas['material_code'] = datas['carton_pallet_id']['material_id']['material_code']
                datas['material_name'] = datas['carton_pallet_id']['material_id']['material_name']
                datas['material_id'] = datas['carton_pallet_id']['material_id']['_id']
                datas['vendor_batch'] = datas['carton_pallet_id']['vendor_batch']
                datas['sap_batch'] = datas['carton_pallet_id']['sap_batch']
                datas['expiry_date'] = VnTimestamp.get_ddmmyyy_to_timestamp(datas['carton_pallet_id']['expiry_date'])
                datas['carton_pallet_id'] = datas['carton_pallet_id']['_id']
                return ApiBase.createResponseMessage(datas, response['msg'])
        return ApiBase.createNotImplement() 
    



class PdaQuarantined(ApiBase):
    """
        Màn hình print Quarantined
    """
    urls = ("/pda/quarantined",)

    def __init__(self) -> None:
        self.__api_backend = CallApiBackEnd()
        self.__create_quarantined = self.__api_backend.createQuarantined
        self.__logger = Logger()
        return super().__init__()

    @ApiBase.exception_error
    def post(self):
        args = ResponseFomat.API_QUARANTINED
        datas = self.jsonParser(args, args)
        response = self.__create_quarantined(datas)
        if response.status_code != 201:
            response = response.json()
            return ApiBase.createResponseMessage({}, response['message'], response['statusCode'], response['statusCode'])
        else:
            response = response.json()
            return ApiBase.createResponseMessage({}, response['msg'])








class StartPalletCarton(ApiBase):
    """
        Start pallet carton
    """
    urls = ("/pallet_carton/start",)

    def __init__(self) -> None:
        self.__api_backend = CallApiBackEnd()

        self.__carton_pallet_start_pallet = self.__api_backend.processEndPalletCarton

        self.__logger = Logger()
        return super().__init__()

    @ApiBase.exception_error
    def post(self):
        # args = ResponseFomat.API_PDA_INPUT
        # datas = self.jsonParser(args, args)
        response = self.__carton_pallet_start_pallet()
        if response.status_code != 201:
            response = response.json()
            return ApiBase.createResponseMessage({}, response['message'], response['statusCode'], response['statusCode'])
        else:
            response = response.json()
            return ApiBase.createResponseMessage({}, response['msg'])
    


