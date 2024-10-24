import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import CFG_MONGODB
from datetime import datetime
from database.models import MissionModel
from config.constants import SETTING_SYSTEM
from database.config_mongo import Collection, DataBaseName
from utils.logger import Logger

class DatabaseConnection:
    def __init__(self):

        # self.__url = 'mongodb://root:jfhe434jc349fj@4.145.80.147:29002/'

        if CFG_MONGODB["username"] and CFG_MONGODB["password"]:
            self.__url = f'mongodb://{CFG_MONGODB["username"]}:{CFG_MONGODB["password"]}@{CFG_MONGODB["host"]}:{CFG_MONGODB["port"]}'
        else:
            self.__url = f'mongodb://{CFG_MONGODB["host"]}:{CFG_MONGODB["port"]}'

        self.client = MongoClient(self.__url)
        self.db = self.client[DataBaseName.DATABASE_FIKA]

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

    def close(self):
        self.client.close()


    def insert_mission_history(self, mission_data: dict) -> ObjectId:
        try:
            collection = self.db.get_collection(Collection.MISSION_HISTORIES)
            result = collection.insert_one(mission_data)
            return result.inserted_id
        except Exception as e:
            Logger().error(f"Error databse: {e}")

    def update_mission_history(self, mission_id, update_data: dict):
        try:
            collection = self.db.get_collection(Collection.MISSION_HISTORIES)
            result = collection.update_one({"_id": ObjectId(mission_id)}, {"$set": update_data})
            return result.modified_count
        except Exception as e:
            Logger().error(f"Error databse: {e}")

    

    def get_setting_systems(self) -> dict:
        """Lấy nhiệm vụ dựa trên mission_code."""
        try:
            setting_systems = {}
            collection = self.get_collection(Collection.SETTING_SYSTEMS)
            
            value_dws_weight  = collection.find_one({"name": "DWS_WEIGHT (g)"})["value"]
            value_dws_size    = collection.find_one({"name": "DWS_SIZE (mm)"})["value"]
            value_interval    = collection.find_one({"name": "Inspection Checking Rate (%)"})["value"]
            
            setting_systems[SETTING_SYSTEM.DWS_WEIGHT]  = float(value_dws_weight)
            setting_systems[SETTING_SYSTEM.DWS_SIZE]    = float(value_dws_size)
            setting_systems[SETTING_SYSTEM.INTERVAL]    = float(value_interval)
            
            return setting_systems
        except Exception as e:
            Logger().error(f"Error databse: {e}")

    
    def get_setting_error_cartons(self) -> list:
        """Lấy nhiệm vụ dựa trên mission_code."""
        try:
            collection = self.get_collection(Collection.SETTING_CARTONS)
            
            # Lấy tất cả các giá trị của trường 'name'
            names = collection.find({}, {"_id": 0, "name": 1})
            # Trả về danh sách các giá trị 'name'
            return [item["name"] for item in names if "name" in item][::-1]
        except Exception as e:
            Logger().error(f"Error databse: {e}")

    

    def get_setting_callbox(self, mission_name: str) -> dict:
        try:
            collection = self.get_collection(Collection.SETTING_CALLBOXES)

            info_mision  = collection.find_one({"task_code": mission_name})
            
            return info_mision
        except Exception as e:
            Logger().error(f"Error databse: {e}")

    
    def get_final_result_carton(self, carton_code: str) -> str:
        try:
            carton_code = carton_code.rstrip(';')
            collection = self.get_collection(Collection.CARTON_STATES)

            info_mision  = collection.find_one({"carton_code": carton_code})
            # print(f"Searching for carton_code: {carton_code}")
            # print(info_mision)
            if info_mision and 'final_result' in info_mision:
                return info_mision["final_result"]
            else:
                return "NG"
        except Exception as e:
            Logger().error(f"Error databse: {e}")
