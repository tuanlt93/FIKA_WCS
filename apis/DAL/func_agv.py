



class CallBackendAGV():
   

    
    
    def create_mission(self, datas):
        """
            request_body: {
                "mission_code": "string",
                "robot_code": "string",
                "pickup_location": "string",
                "return_location": "string",
                "sector": "Pallet bán thành phẩm",
                "object_call": "string",
                "current_state": "registered"
            }
        """
        try:
            headers = self.__token_value
            url = self.__url_db + self.__mission_history
            response = requests.post(url ,json= datas, headers = headers)
            print("response", response.text, response.url)
            return response
        except Exception as e:
            print("error get_callbox", e)
            return None
        

 
 
    
    def send_mission(self, request_pda):
        """
            request_pda: {
                "tasks": [
                    {
                        "button_id": "TC_1",
                        "action": 1
                    }
                ]
            }
            B1: Tìm callboxes
            B2: Tạo mission
            B3: Bắn lên GMS
            B4: Đẩy vào trigger mission
        """
        try:
            request_pda["callboxes_code"] = f'{request_pda["callboxes_code"]}'
            if request_pda["action"] == 1:
                callbox_data = self.get_callbox(request_pda)
                print("callbox_data :", callbox_data)
                if 'metaData' not in callbox_data:
                    return callbox_data
                list_point = [callbox_data['metaData']['pickup_location'], callbox_data['metaData']['return_location']]
                # Tạo mission
                mission_info_data = {
                    "mission_code": self.create_mission_code(request_pda["callboxes_code"]),
                    # "robot_code": "string",
                    "pickup_location": list_point[0],
                    "return_location": list_point[1],
                    "sector": callbox_data['metaData']['sector'],
                    "object_call": request_pda["callboxes_code"],
                    "current_state": MissionStatus.SIGN
                }
                mission_db = self.create_mission(mission_info_data)
                print("mission_db :", mission_db.text)
                # mission_info_data = self.__create_mission(mission_info_)
                if mission_db.status_code == 201:
                    mission_json = mission_db.json()
                    mission_data = mission_json['metaData']
                    self.trigger_mission(request_pda, mission_data, callbox_data)
                return mission_db.json()
            else:
                pass
                # data = {
                #     "deviceId" : request_pda["tasks"][0]["button_id"],
                #     "plc_id" : request_pda["plc_id"]
                # }
                # callbox_info = __mongodb.get_info_callbox(data)
                # mission_db = __mongodb.query_mission({
                #     "current_state" :  {"$nin": [MissionStatus.CANCEL, MissionStatus.DONE]},
                #     "call_boxes_id" : str(callbox_info["_id"])
                # })
        except Exception as e:
            print("error send_mission", e)
            return True
        