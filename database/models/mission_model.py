from datetime import datetime

class MissionModel:
    def __init__(self, 
                 mission_code, 
                 robot_code, 
                 pickup_location, 
                 return_location, 
                 sector, 
                 object_call, 
                 mission_rcs, 
                 current_state, 
                 created_at,  
                 description="", 
                 updated_at=""
            ):
        
        self.__mission_code = mission_code
        self.__robot_code = robot_code
        self.__pickup_location = pickup_location
        self.__return_location = return_location
        self.__sector = sector
        self.__object_call = object_call  
        self.__mission_rcs = mission_rcs
        self.__description = description
        self.__current_state = current_state
        self.__created_at = created_at
        self.__updated_at = updated_at

    def to_dict(self):
        return {
            "mission_code": self.__mission_code,
            "robot_code": self.__robot_code,
            "pickup_location": self.__pickup_location,
            "return_location": self.__return_location,
            "sector": self.__sector,
            "object_call": self.__object_call.isoformat() if isinstance(self.__object_call, datetime) else "",
            "mission_rcs": self.__mission_rcs,
            "description": self.__description,
            "current_state": self.__current_state,
            "createdAt": self.__created_at.isoformat() if isinstance(self.__created_at, datetime) else "",
            "updatedAt": self.__updated_at.isoformat() if isinstance(self.__updated_at, datetime) else "",
        }

