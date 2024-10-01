import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import CFG_MONGODB, CFG_DATABASE_NAME
from datetime import datetime
from database.models import MissionModel
from config.constants import SETTING_SYSTEM

class DatabaseConnection:
    def __init__(self):

        # self.__url = 'mongodb://root:jfhe434jc349fj@4.145.80.147:29002/'
        self.__url = 'mongodb://localhost:27017/'

        # if CFG_MONGODB['username'] and CFG_MONGODB['password']:
        #     self.__url = f'mongodb://{CFG_MONGODB['username']}:{CFG_MONGODB['password']}@{CFG_MONGODB['host']}:{CFG_MONGODB['port']}'
        # else:
        #     self.__url = f'mongodb://{CFG_MONGODB['host']}:{CFG_MONGODB['port']}'
        self.client = MongoClient(self.__url)

        self.db = self.client[CFG_DATABASE_NAME]

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

    def close(self):
        self.client.close()


    def insert_mission_history(self, mission_data: dict):
        collection = self.db.get_collection('missionhistories')
        result = collection.insert_one(mission_data)
        return result.inserted_id

    def update_mission_history(self, mission_id, update_data: dict):
        collection = self.db.get_collection('missionhistories')
        result = collection.update_one({"_id": ObjectId(mission_id)}, {"$set": update_data})
        return result.modified_count
    

    def get_setting_systems(self) -> dict:
        """Lấy nhiệm vụ dựa trên mission_code."""
        setting_systems = {}
        collection = self.get_collection('settingsystems')
        
        value_dws_weight  = collection.find_one({"name": "DWS_WEIGHT (g)"})["value"]
        value_dws_size    = collection.find_one({"name": "DWS_SIZE (mm)"})["value"]
        value_interval    = collection.find_one({"name": "Inspection Checking Rate (%)"})["value"]
        
        setting_systems[SETTING_SYSTEM.DWS_WEIGHT]  = float(value_dws_weight)
        setting_systems[SETTING_SYSTEM.DWS_SIZE]    = float(value_dws_size)
        setting_systems[SETTING_SYSTEM.INTERVAL]    = float(value_interval)
        
        return setting_systems