# from utils.decorator import exception_handler
import requests
from db_redis import redis_cache
from config.constants import HandlePalletConfig, STATUS_PALLET_CARTON, HandleCartonConfig, SETTING_SYSTEM
from config.config_apis import ConfigAPI
from apis.DAL import dal_server
from apis.response_format import ResponseFomat
import json
from PLC import PLC_controller
from database import db_connection

# class CallApiBackEnd(metaclass=Singleton):
class CallApiBackEnd():
    def __init__(self) -> None:
        self.__dal_server = dal_server
        self.__get_token_bearer = self.__dal_server.get_token_bearer()
        self.__redis_cache = redis_cache
        self.__PLC_controller = PLC_controller
        self.__db_connection = db_connection


        
        self.__url = ConfigAPI.url
        self.__url_datamax  = ConfigAPI.url_print_datamax

        # Pallet carton
        self._pallet_carton = ConfigAPI.pallet_carton
        self._carton_pallet_create = ConfigAPI.carton_pallet_create
        self._carton_pallet_start_pallet = ConfigAPI.carton_pallet_start_pallet
        self._carton_pallet_change_status = ConfigAPI.carton_pallet_change_status
        self._carton_pallet_update_visa = ConfigAPI.carton_pallet_update_visa
        self._carton_pallet_dws_info = ConfigAPI.carton_pallet_dws_info

        # Carton State
        self._carton_state_info = ConfigAPI.carton_state_info
        self._carton_state_printer = ConfigAPI.carton_state_printer
        self._carton_state_dws = ConfigAPI.carton_state_dws
        self._carton_state_confirm_qty = ConfigAPI.carton_state_confirm_qty
        self._carton_pallet_code_info = ConfigAPI.carton_pallet_code_info
        self._carton_state_get_input = ConfigAPI.carton_state_get_input
        self._carton_state_change_status = ConfigAPI.carton_state_change_status
        self._carton_state_find_material = ConfigAPI.carton_state_find_material
        self._carton_state_code_info = ConfigAPI.carton_state_code_info

        # Carton error
        self._carton_state_input_error = ConfigAPI.carton_error_input

        # Carton Qty
        self._carton_qty = ConfigAPI.carton_qty
        self._carton_qty_info = ConfigAPI.carton_qty_info
        self._carton_qty_create = ConfigAPI.carton_qty_create
        self._carton_qty_update = ConfigAPI.carton_qty_update

        #Setting system
        self._setting_system_info = ConfigAPI.setting_system_info

        self._carton_state = ConfigAPI.carton_state
        self._carton_qty = ConfigAPI.carton_qty
        self._carton_error = ConfigAPI.carton_error
        self._material = ConfigAPI.material
        self._setting_carton = ConfigAPI.setting_carton
        self._setting_system = ConfigAPI.setting_system
        self._setting_call_boxes = ConfigAPI.setting_call_boxes
        self._setting_call_boxes_info = ConfigAPI.setting_call_boxes_info

        # Mission
        self._mission_info = ConfigAPI.mission_info
        self._mission_history = ConfigAPI.mission_history
        self._mission_status = ConfigAPI.mission_status

        # Device status
        self._device_status = ConfigAPI.device_status
        self._device_status_update = ConfigAPI.device_status_update

        # Pda history
        self._pda_history = ConfigAPI.pda_history
        # Quaratined
        self._quarantined_create = ConfigAPI.quarantined_create




    # # @exception_handler
    def createPallet(self, mision_name: str):
        """
            Tạo mới Pallet -> Tạo mới material (if not available) -> Tạo mới CartonQty (if not available):
            response = {
                'msg': 'Tạo mới thành công',
                "metaData": {
                    "material_id":{
                        "_id":"66cb534dcb5be5b2b05b7f93",
                        "material_code":"211926128",
                        "material_name":"Thuốc đau đầu",
                        "stt_pallet":3,
                        "createdAt":"2024-08-25T15:52:45.825Z",
                        "updatedAt":"2024-08-25T17:24:17.435Z",
                        "__v":0
                        },
                    "carton_pallet_code":"211926128,SHJKL,20240530,3,30",
                    "vendor_batch":"SHJKL",
                    "sap_batch":"F-SHJKL",
                    "expiry_date":"09/07/2025",
                    "layer_pallet":4,
                    "carton_pallet_qty":30,
                    "standard_length": 400,
                    "standard_width": 250,
                    "standard_height": 200,

                    "standard_weight":10,
                    "standard_item_carton":100,
                    "stt_carton":0,
                    "status":"pending",
                    "_id":"66cb6949cb5be5b2b05b7ff0", 
                    "createdAt":"2024-08-25T17:26:33.019Z",
                    "updatedAt":"2024-08-25T17:26:33.019Z",
                    "__v":0
                }
            }
            --> sửa lại data pda gửi lên
            --> OKE
        """
        headers = self.__get_token_bearer
        datas = json.loads(self.__redis_cache.hget(
            HandlePalletConfig.PALLET_DATA_MANAGEMENT, 
            HandlePalletConfig.PALLET_INPUT_DATA   
        ))
        response = requests.post(self.__url + self._carton_pallet_create, json = datas, headers = headers)
        print(response.text)

        if response.status_code == 201:
            response_data = response.json()
            print(response_data)
            print(type(response_data))
            material_id = response_data['metaData']['material_id']["_id"]
            self.createCartonQty(material_id)


            datas["carton_pallet_code"] = response_data['metaData']["carton_pallet_code"]
            datas["_id"] = response_data['metaData']["_id"]


            # #TODO :  đưa lấy thông tin kích thước sang tạo mới pallet
            # carton_pallet_dws = self.getDwsPalletCarton(datas["_id"]).json()
            # print(carton_pallet_dws)
            # data_system = self.map_system(carton_pallet_dws['data_system'])
            
            # print(data_system)
            setting_systems = self.__db_connection.get_setting_systems()

            if setting_systems:
                self.__redis_cache.set(
                        SETTING_SYSTEM.TOPIC_SETTING_SYSTEM, 
                        json.dumps(setting_systems)
                    )

            # Lưu data pallet có được vào redis
            if mision_name == "MISSION_A1":
                

                print("Done send dimension to PLC")
                self.__redis_cache.hset(
                    HandlePalletConfig.PALLET_DATA_MANAGEMENT, 
                    HandlePalletConfig.PALLET_INPUT_A1_DATA, 
                    json.dumps(datas)
                )
                self.__PLC_controller.send_info_pallet_A1(response_data['metaData'])

            elif mision_name == "MISSION_A2":
                print("Done send dimension to PLC")
                self.__redis_cache.hset(
                    HandlePalletConfig.PALLET_DATA_MANAGEMENT, 
                    HandlePalletConfig.PALLET_INPUT_A2_DATA, 
                    json.dumps(datas)
                )
                self.__PLC_controller.send_info_pallet_A2(response_data['metaData'])

            self.__redis_cache.hdel(
                HandlePalletConfig.PALLET_DATA_MANAGEMENT, 
                HandlePalletConfig.PALLET_INPUT_DATA   
            )
            
        return response
    
    def map_system(self, datas):
        out_data = {    }
        for data in datas:
            out_data[data['name']] = float(data['value'])
        return out_data


    # @exception_handler
    def createCartonQty(self, material_id):
        """
            Tạo mới CartonQty (if not available)
            response = {
                'msg': 'Tạo mới thành công',
                "metaData": {
                    "material_id":{
                        "_id":"66cb534dcb5be5b2b05b7f93",
                        "material_code":"211926128",
                        "material_name":"Thuốc đau đầu",
                        "stt_pallet":1,
                        "createdAt":"2024-08-25T15:52:45.825Z",
                        "updatedAt":"2024-08-25T15:52:45.825Z",
                        "__v":0
                    },
                    "input_qty":0,
                    "final_qty":0,
                    "final_ok_qty":0,
                    "final_ng_qty":0,
                    "description":"",
                    "_id":"66cb534dcb5be5b2b05b7f9a",
                    "createdAt":"2024-08-25T15:52:45.894Z",
                    "updatedAt":"2024-08-25T15:52:45.894Z",
                    "__v":0
                }
            }
            ---> OKE
        """
        headers = self.__get_token_bearer
        url = self.__url + self._carton_qty_create
        datas = {
            "material_id" : material_id
        }
        response = requests.post(url ,json= datas, headers = headers)
        # print(response.text)
        # print("--------------")
        return response

    

    def createCarton(self, datas: ResponseFomat.API_CREATE_CARTON_STATE):
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
        headers = self.__get_token_bearer
        url = self.__url + self._carton_state_dws
        # print(datas)
        response = requests.post(url, json = datas, headers = headers)
        if response.status_code == 201:
            response = response.json()
        return response



    # @exception_handler
    def startPalletCarton(self):
        """
            Bắt đầu pallet carton mới
            --- > OKE
        """
        headers = self.__get_token_bearer
        url = self.__url + self._carton_pallet_start_pallet
        myobj = {}
        response = requests.post(url, json = myobj, headers = headers)
        if response.status_code == 201:
            data_redis = response.json()
        return response
    

    def getCartonPalletCode(self, datas):
        """
            Thay đổi trạng thái carton theo id (ko sử dụng)
            {
                dws_result? : ",
                inspection_result? : ",
                correction_result? : "
            }
        """
        headers = self.__get_token_bearer
        params={
            "carton_pallet_code": datas['pallet_code']
        }
        url = self.__url + self._carton_pallet_code_info
        response = requests.get(url ,params = params, headers = headers)
        return response





    # def processEndPalletCarton(self):
    #     """
    #         Bắt đầu 1 pallet mới và kết thúc pallet cũ 
    #         ()
    #     """
    #     headers = self.__get_token_bearer
    #     _id = self._redis.get_key(TOPIC_REDIS.PALLET_CARTON_RUN, "_id")
    #     response_end = self.UpdateSttPalletCarton(_id)
    #     print(response_end)
    #     url_start = self.__url + self._carton_pallet_start_pallet
    #     myobj = {}
    #     response_start = requests.post(url_start, json = myobj, headers = headers)
    #     print("response_start :", response_start)
    #     if response_start.status_code == 201:
    #         data_redis = response_start.json()
    #         self._redis.set_dict(TOPIC_REDIS.PALLET_CARTON_RUN, data_redis['metaData'])
    #     return response_start
    

    
    # @exception_handler
    def UpdateSttPalletCarton(self, id):
        """
            Kết thúc pallet carton
        """
        try:
            headers = self.__get_token_bearer
            url = self.__url + self._carton_pallet_change_status + id
            myobj = {"status" : STATUS_PALLET_CARTON.DONE}
            response = requests.post(url, json = myobj, headers = headers)

            # Xóa data pallet đang chạy và reset số lượng DWS
            self.__redis_cache.delete_first_element(HandlePalletConfig.LIST_PALLET_RUNNING)
            self.__redis_cache.hset(HandlePalletConfig.NUMBER_CARTON_OF_PALLET, HandlePalletConfig.QUANTITY_FROM_DWS, 0)
            return response
        except Exception as e:
            print("UpdateSttPalletCarton :", e)
            return None


    # @exception_handler
    def getDwsPalletCarton(self, id):
        """
            Lấy thông tin sai số, và thông tin về pallet
        """
        headers = self.__get_token_bearer
        url = self.__url + self._carton_pallet_dws_info + id
        response = requests.get(url, headers = headers)
        return response
    




    # Carton
    def cartonInfo(self, id):
        """
            Lấy thông tin carton
        """
        headers = self.__get_token_bearer
        url = self.__url + self._carton_state_info + id
        response = requests.get(url, headers = headers)
        return response
    

    def getCartonStateCode(self, datas):
        """
            Lấy thông tin để in tem
        """
        headers = self.__get_token_bearer
        params={
            "carton_code": datas['carton_code']
        }
        url = self.__url + self._carton_state_code_info
        response = requests.get(url ,params = params, headers = headers)
        return response
    


    def cartonPrinter(self):
        """
            Lấy thông tin carton đã in trước đấy
        """
        headers = self.__get_token_bearer
        url = self.__url+self._carton_state_printer
        response = requests.get(url , headers = headers)
        return response
    


    def findMaterialByCartonState(self, id):
        """
            Lấy thông tin material theo carton id
        """
        headers = self.__get_token_bearer
        url = self.__url+self._carton_state_find_material + id
        response = requests.get(url , headers = headers)
        return response
    

    
    


    def getInputInsectionOrCorrection(self, datas: ResponseFomat.API_CARTON_STATE_INPUT_ERROR):
        """
            Tao moi 1 luong chay qc carton
            {
                "carton_code": "string",
                "type_result": "string" 
            }
            type_result: inspection, correction
        """
        headers = self.__get_token_bearer
        url = self.__url + self._carton_state_get_input
        response = requests.get(url, params = datas, headers = headers)
        # print(response.text)
        return response


    def inputInsectionOrCorrection(self, datas: ResponseFomat.API_CARTON_STATE_INPUT_ERROR):
        """
            Tao moi 1 luong chay qc carton
            {
                "carton_code": "string",
                "type_result": "string" 
            }
            type_result: inspection, correction
        """
        headers = self.__get_token_bearer
        url = self.__url + self._carton_state_input_error
        response = requests.post(url, json = datas, headers = headers)
        return response
    


    def finalCartonState(self, carton_state_id, data_state):
        """
            Update số lượng carton qty và carton state
            Nếu dws_result ok hoặc inspection_result ok hoặc correction_result thì gọi hàm
            - data_state:
                dws_result? : ",
                inspection_result? : ",
                correction_result? : ",
                final_result? : ",
            - data_qty: 
                final_qty? : 0,
                final_ok_qty? : 0,
                final_ng_qty? : 0
        """
        try:
            data_qty = {}
            data_dict = data_state.copy()
            for data in data_state:
                data_dict['final_result'] = data_state[data]
                if data_dict[data] == HandleCartonConfig.OK:
                    data_qty['final_ok_qty'] = 1
                    break
                else:
                    data_qty['final_ng_qty'] = 1
            data_qty['final_qty'] = 1
            data_material = self.findMaterialByCartonState(carton_state_id)
            data_material = data_material.json()
            material_id = data_material['metaData']['_id']
            data_update = self.updateState(carton_state_id, data_dict)
            self.updateCartonQty(material_id, data_qty)
            if data_update.status_code == 200:
                data_update = data_update.json()
                data_carton_state = data_update['data']
                self.__redis_cache.del_key(TOPIC_REDIS.CARTON_INFO + data_carton_state['carton_code'])
        except Exception as e:
            print( "finalCartonState :", e)


    

    # @exception_handler
    def updateCartonQty(self, material_id, datas):
        """
            Update số lượng carton theo id
            {
                input_qty : 0,
                final_qty? : 0,
                final_ok_qty? : 0,
                final_ng_qty? : 0
            }
        """
        headers = self.__get_token_bearer
        url_info = self.__url + self._carton_qty_info 
        response = requests.get(url_info ,params = {"material_id": material_id} , headers = headers)
        if response.status_code == 200:
            response = response.json()
            meta_data = response['metaData']
            # out_data = {}
            # for data in datas:
            #     out_data[data] = int(datas[data]) + int(meta_data[data])
            url_update = self.__url + self._carton_qty_update + meta_data['_id']
            print("updateCartonQty :", meta_data['_id'], datas)
            response = requests.patch(url_update ,json= datas, headers = headers)
            return response
        return None

    def updateState(self, id, datas):
        """
            Thay đổi trạng thái carton theo id
            {
                dws_result? : ",
                inspection_result? : ",
                correction_result? : ",
                final_result? : ",
            }
        """
        headers = self.__get_token_bearer
        url = self.__url + self._carton_state_change_status + id
        response = requests.patch(url ,json= datas, headers = headers)
        return response
    



    def confirmCartonState(self, datas):
        """
            Màn hình confirm số lượng qty
        """
        headers = self.__get_token_bearer
        url = self.__url + self._carton_state_confirm_qty
        response = requests.post(url ,json= datas, headers = headers)
        return response



    def updateVisa(self, id, datas):
        """
            Update visa của pallet carton theo id
            {
                visa: ''
            }
        """
        headers = self.__get_token_bearer
        url = self.__url + self._carton_pallet_update_visa + id
        response = requests.patch(url ,json= datas, headers = headers)
        print(response.text)
        return response






    def palletInfo(self, id: str):
        """
            Lấy thông tin pallet theo id
            {
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
        """
        headers = self.__get_token_bearer
        url = self.__url + self._pallet_carton + id
        response = requests.get(url , headers = headers)
        return response
    
    def dwsInfo(self, id):
        """
            Lấy thông tin pallet theo id và kèm theo setting_system cho dws trong 1 resquest
        """
        headers = self.__get_token_bearer
        url = self.__url + self._pallet_carton + id
        response = requests.get(url , headers = headers)
        return response

    def checkQtyCarton(self, id):
        """
            Kiểm tra số lượng carton theo id
        """
        headers = self.__get_token_bearer
        url = self.__url + self._pallet_carton + id
        response = requests.get(url , headers = headers)
        return response

    def callBoxesInfoAll(self):
        """
            Lấy thông tin tất cả bộ gọi
        """
        headers = self.__get_token_bearer
        url = self.__url + self._setting_call_boxes
        response = requests.get(url , headers = headers)
        return response
    
    def callBoxesInfo(self, data):
        """
            Lấy thông tin bộ gọi
            {
                "callboxes_code" : ""
            }
        """
        headers = self.__get_token_bearer
        url = self.__url + self._setting_call_boxes_info
        response = requests.get(url , params=data, headers = headers)
        return response

    # Quarantined
    def createQuarantined(self, datas):
        headers = self.__get_token_bearer
        url = self.__url + self._quarantined_create
        response = requests.post(url ,json= datas, headers = headers)
        return response

    # Mission
    def getMissionInfo(self, data):
        """
            Lấy thông tin nhiệm vụ robot theo mission_code
            ok
        """
        headers = self.__get_token_bearer
        url = self.__url + self._mission_info
        response = requests.get(url , params = data, headers = headers)
        return response

    def getStatusMission(self, datas):
        """
            Lấy trạng thái nhiệm vụ robot theo current_state
            {
                "current_state" : ''
            }
            ok
        """
        headers = self.__get_token_bearer
        url = self.__url + self._mission_status
        params = datas
        response = requests.get(url , params,  headers = headers)
        return response

    def updateMission(self, datas):
        """
            Update trạng thái nhiệm vụ robot
            {
                "robot_code" : '',
                "sector" : '',
                "mission_rcs" : '',
                "call_boxes_id" : '',
                "current_state" : '',
                "mission_code : '
            }
            ok
        """
        headers = self.__get_token_bearer
        url = self.__url + self._mission_history
        if 'mission_code' in datas:
            datas["filter"] = {
                "mission_code" : datas['mission_code']
            }
            datas.pop("mission_code")
        elif 'mission_rcs' in datas:
            datas["filter"] = {
                "mission_rcs" : datas['mission_rcs']
            }
            datas.pop("mission_rcs")
        response = requests.patch(url ,json= datas, headers = headers)
        return response

    def updateStatusMission(self, datas):
        """
            Update trạng thái nhiệm vụ robot
            {
                "mission_rcs" : '',
                "mission_code" : '',
                "current_state" : ''

            }
            ok
        """
        headers = self.__get_token_bearer
        url = self.__url + self._mission_history
        if 'mission_code' in datas:
            datas["filter"] = {
                "mission_code" : datas['mission_code']
            }
            datas.pop("mission_code")
        elif 'mission_rcs' in datas:
            datas["filter"] = {
                "mission_rcs" : datas['mission_rcs']
            }
            datas.pop("mission_rcs")
        response = requests.patch(url ,json= datas, headers = headers)
        return response

    def updateStatusDevice(self, datas):
        """
            Cập nhật trạng thái cho thiết bị
            {
                "device_id" : string,
                "status" : boolean

            }
        """
        headers = self.__get_token_bearer
        url = self.__url + self._device_status_update
        response = requests.patch(url ,json= datas, headers = headers)
        return response
    
    # Setting system
    def getSettingSystem(self):
        """
            Lấy trạng thái nhiệm vụ robot theo current_state
            {
                "current_state" : ''
            }
            ok
        """
        headers = self.__get_token_bearer
        url = self.__url + self._setting_system_info
        response = requests.get(url , headers = headers)
        return response
    
    # Pda History
    def pdaHistory(self, datas, token):
        """
            Lấy lịch sử pda
            {
                "pda_code" : ''
            }
        """
        data_history = {
            "carton_code": datas['carton_state_code'],
            "location": datas["type_error"],
            "result": datas['result']
        }
        headers = {
            "Authorization": token
        }
        url = self.__url + self._pda_history
        response = requests.post(url , json=data_history, headers = headers)
        return response
    


    def sendPrintDatamax(self, data: dict):
        """
            Gửi dữ liệu đến máy in datamax
        """
        headers = self.__get_token_bearer
        url = self.__url_datamax
        response = requests.post(url= url, json= data)
        return response