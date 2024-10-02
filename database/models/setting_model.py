from datetime import datetime

class SettingCallBoxModel:
    def __init__(self, 
                 task_code, 
                 name, 
                 pickup_location, 
                 return_location,  
                 created_at, 
                 updated_at
            ):
        self.__task_code = task_code
        self.__name = name  
        self.__pickup_location = pickup_location
        self.__return_location = return_location
        self.__created_at = created_at
        self.__updated_at = updated_at

    def to_dict(self):
        return {
            "task_code": self.__task_code,
            "name": self.__name,
            "pickup_location": self.__pickup_location,
            "return_location": self.__return_location,
            "createdAt": self.__created_at.isoformat() if isinstance(self.__created_at, datetime) else "",
            "updatedAt": self.__updated_at.isoformat() if isinstance(self.__updated_at, datetime) else "",
        }



class SettingCartonsModel:
    def __init__(self, 
                 task_code, 
                 name, 
                 description,
                 created_at, 
                 updated_at
            ):
        self.__task_code = task_code
        self.__name = name  
        self.__description = description
        self.__created_at = created_at
        self.__updated_at = updated_at

    def to_dict(self):
        return {
            "task_code": self.__task_code,
            "name": self.__name,
            "description": self.__description,
            "createdAt": self.__created_at.isoformat() if isinstance(self.__created_at, datetime) else "",
            "updatedAt": self.__updated_at.isoformat() if isinstance(self.__updated_at, datetime) else "",
        }
    

class SettingSystemsModel:
    def __init__(self,  
                 name, 
                 value,
                 created_at, 
                 updated_at
            ):
        self.__name = name  
        self.__value = value
        self.__created_at = created_at
        self.__updated_at = updated_at

    def to_dict(self):
        return {
            "name": self.__name,
            "value": self.__value,
            "createdAt": self.__created_at.isoformat() if isinstance(self.__created_at, datetime) else "",
            "updatedAt": self.__updated_at.isoformat() if isinstance(self.__updated_at, datetime) else "",
        }