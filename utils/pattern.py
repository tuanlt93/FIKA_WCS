import threading
from typing import Type

class Singleton(type):
    """
    Create a class which only init once
    Instruction:
        class foo(metaclass=Singleton)
    """
    _instance = {}
    _lock = threading.Lock()
    def __call__(cls, *args, **kwds):
        if cls not in cls._instance:
            with cls._lock:
                if cls not in cls._instance:
                    instance = super().__call__(*args, **kwds)
                    cls._instance[cls] = instance
        return cls._instance[cls]

#TODO: Orther
# # plc/plc_controller.py
# class PLCController:
#     _instance = None

#     def __new__(cls, ip, port):
#         if cls._instance is None:
#             cls._instance = super(PLCController, cls).__new__(cls)
#             cls._instance.ip = ip
#             cls._instance.port = port
#             cls._instance.connect()
#         return cls._instance

#     def connect(self):
#         # Kết nối đến PLC
#         print(f"Connecting to PLC at {self.ip}:{self.port}")

#     # Các phương thức khác


from enum import Enum

class Custom_Enum(Enum):
    @classmethod
    def keys(cls) -> list:
        return cls._member_names_

    @classmethod
    def values(cls) -> list:
        return list(cls._value2member_map_.keys())

    @classmethod
    def list(cls) -> list:
        return list(cls)

    @classmethod
    def dict(cls) -> dict:
        return cls._member_map_

    @classmethod
    def index(cls, item: Type["Enum | str"]) -> int:
        """
        :item: can be member or name
        """
        if type(item) != str:
            item = item.name
        return cls._member_names_.index(item)

    @classmethod
    def get(cls, index: int):
        """
        Return value from index
        """
        return cls.values()[index]




# class Logger(metaclass=Singleton):
#     def __init__(self):
#         print("Logger initialized")

# logger1 = Logger()
# logger2 = Logger()

# assert logger1 is logger2  # Both are the same instance


# class Color(Custom_Enum):
#     RED = 1
#     GREEN = 2
#     BLUE = 3

# print(Color.keys())    # ['RED', 'GREEN', 'BLUE']
# print(Color.values())  # [1, 2, 3]
# print(Color.list())    # [<Color.RED: 1>, <Color.GREEN: 2>, <Color.BLUE: 3>]
# print(Color.dict())    # {'RED': <Color.RED: 1>, 'GREEN': <Color.GREEN: 2>, 'BLUE': <Color.BLUE: 3>}
# print(Color.index('GREEN'))  # 1
# print(Color.get(2))         # 3
