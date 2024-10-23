from config.constants import DeviceConfig, AGVConfig, HandlePalletConfig
from apis.api_base import ApiBase
from utils.logger import Logger
from db_redis import redis_cache


class MonitorMission(ApiBase):
    """
        response = { 
            "MISSION_A1": ["Dock A1 chưa sẵn sàng", "Thang máy lên chưa sẵn sàng"], 
            "MISSION_A2": ["Dock A1 chưa sẵn sàng", "Thang máy lên chưa sẵn sàng", "Thang máy lên chưa sẵn sàng", "Thang máy lên chưa sẵn sàng", "Thang máy lên chưa sẵn sàng"], 
            "MISSION_A3": ["Dock A1 chưa sẵn sàng"],
            "MISSION_O1": ["Dock A1 chưa sẵn sàng"],
            "MISSION_O2": ["Dock A1 chưa sẵn sàng"],
            "MISSION_O3": ["Dock A1 chưa sẵn sàng"],
            "MISSION_M1": ["Dock A1 chưa sẵn sàng"],
            "MISSION_M2": ["Dock A1 chưa sẵn sàng"],
            "MISSION_M3": ["Dock A1 chưa sẵn sàng"],
            "MISSION_M4": ["Dock A1 chưa sẵn sàng"]
        }
    """
    urls = ("/data/monitor/agv",)

    def __init__(self) -> None:
        self.__redis_cache = redis_cache
        
        super().__init__()

    @ApiBase.exception_error
    def get(self):
        response = { 
            "MISSION_A1": [], 
            "MISSION_A2": [], 
            "MISSION_A3": [],
            "MISSION_O1": [],
            "MISSION_O2": [],
            "MISSION_O3": [],
            "MISSION_M1": [],
            "MISSION_M2": [],
            "MISSION_M3": [],
            "MISSION_M4": []
        }
        self.__running_tasks        = self.__redis_cache.smembers(AGVConfig.MISSIONS_RUNNING)
        self.__status_all_device    = self.__redis_cache.hgetall(DeviceConfig.STATUS_ALL_DEVICES)
        self.__device_agv_used      = self.__redis_cache.hgetall(AGVConfig.ALL_AGV_DEVICE_USED)
        self.__data_pallet_input    = self.__redis_cache.hgetall(HandlePalletConfig.PALLET_DATA_MANAGEMENT)       

        for key in response:
                if key == "MISSION_A1":
                    if key in self.__running_tasks:
                        response[key].append("ĐANG THỰC HIỆN")
                    else:
                        if self.__status_all_device[DeviceConfig.STATUS_DOCK_A1] != DeviceConfig.DOCK_EMPTY:
                            response[key].append("Dock A1 đang có pallet")
                        if self.__status_all_device[DeviceConfig.STATUS_ELEVATOR_LIFTING_UP] != DeviceConfig.ELEVATOR_LIFTING_READY:
                            response[key].append("Trạng thái thang máy lên đang bận")

                        if self.__device_agv_used[DeviceConfig.STATUS_DOCK_A1] != AGVConfig.DONT_USE:
                            response[key].append("Dock A1 đang được AGV sử dụng")
                        if self.__device_agv_used[DeviceConfig.STATUS_ELEVATOR_LIFTING_UP] != AGVConfig.DONT_USE:
                            response[key].append("Thang máy lên AGV đang sử dụng")
                        
                        if self.__data_pallet_input.get(HandlePalletConfig.INPUT_PALLET_DATA) is None:
                            response[key].append("Chưa có dữ liệu QR đầu vào")
                
                elif key == "MISSION_A2":
                    if key in self.__running_tasks:
                        response[key].append("ĐANG THỰC HIỆN")
                    else:
                        if self.__status_all_device[DeviceConfig.STATUS_DOCK_A2] != DeviceConfig.DOCK_EMPTY:
                            response[key].append("Dock A2 đang có pallet")
                        if self.__status_all_device[DeviceConfig.STATUS_ELEVATOR_LIFTING_UP] != DeviceConfig.ELEVATOR_LIFTING_READY:
                            response[key].append("Trạng thái thang máy lên đang bận")

                        if self.__device_agv_used[DeviceConfig.STATUS_DOCK_A2] != AGVConfig.DONT_USE:
                            response[key].append("Dock A2 đang được AGV sử dụng")
                        if self.__device_agv_used[DeviceConfig.STATUS_ELEVATOR_LIFTING_UP] != AGVConfig.DONT_USE:
                            response[key].append("Thang máy lên AGV đang sử dụng")

                        if self.__data_pallet_input.get(HandlePalletConfig.INPUT_PALLET_DATA) is None:
                            response[key].append("Chưa có dữ liệu QR đầu vào")
                
                elif key == "MISSION_A3":
                    if key in self.__running_tasks:
                        response[key].append("ĐANG THỰC HIỆN")
                    else:
                        if self.__status_all_device[DeviceConfig.STATUS_DOCK_A3] != DeviceConfig.DOCK_FULL:
                            response[key].append("Dock A3 chưa đầy")
                        if self.__status_all_device[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != DeviceConfig.ELEVATOR_LIFTING_READY:
                            response[key].append("Trạng thái thang máy xuống đang bận")

                        if self.__device_agv_used[DeviceConfig.STATUS_DOCK_A3] != AGVConfig.DONT_USE:
                            response[key].append("Dock A3 đang được AGV sử dụng")
                        if self.__device_agv_used[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != AGVConfig.DONT_USE:
                            response[key].append("Thang máy xuống AGV đang sử dụng")


                elif key == "MISSION_O1":
                    if key in self.__running_tasks:
                        response[key].append("ĐANG THỰC HIỆN")
                    else:
                        if self.__status_all_device[DeviceConfig.STATUS_DOCK_O1] != DeviceConfig.DOCK_FULL:
                            response[key].append("Dock O1 chưa đầy")
                        if self.__status_all_device[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != DeviceConfig.ELEVATOR_LIFTING_READY:
                            response[key].append("Trạng thái thang máy xuống đang bận")

                        if self.__device_agv_used[DeviceConfig.STATUS_DOCK_O1] != AGVConfig.DONT_USE:
                            response[key].append("Dock O1 đang được AGV sử dụng")
                        if self.__device_agv_used[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != AGVConfig.DONT_USE:
                            response[key].append("Thang máy xuống AGV đang sử dụng")
                
                elif key == "MISSION_O2":
                    if key in self.__running_tasks:
                        response[key].append("ĐANG THỰC HIỆN")
                    else:
                        if self.__status_all_device[DeviceConfig.STATUS_DOCK_O2] != DeviceConfig.DOCK_FULL:
                            response[key].append("Dock O2 chưa đầy")
                        if self.__status_all_device[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != DeviceConfig.ELEVATOR_LIFTING_READY:
                            response[key].append("Trạng thái thang máy xuống đang bận")

                        if self.__device_agv_used[DeviceConfig.STATUS_DOCK_O2] != AGVConfig.DONT_USE:
                            response[key].append("Dock O2 đang được AGV sử dụng")
                        if self.__device_agv_used[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != AGVConfig.DONT_USE:
                            response[key].append("Thang máy xuống AGV đang sử dụng")

                elif key == "MISSION_O3":
                    if key in self.__running_tasks:
                        response[key].append("ĐANG THỰC HIỆN")
                    else:
                        if self.__status_all_device[DeviceConfig.STATUS_DOCK_O3] != DeviceConfig.DOCK_EMPTY:
                            response[key].append("Dock O3 đang có pallet")
                        if self.__status_all_device[DeviceConfig.STATUS_ELEVATOR_LIFTING_UP] != DeviceConfig.ELEVATOR_LIFTING_READY:
                            response[key].append("Trạng thái thang máy lên đang bận")

                        if self.__device_agv_used[DeviceConfig.STATUS_DOCK_O3] != AGVConfig.DONT_USE:
                            response[key].append("Dock O3 đang được AGV sử dụng")
                        if self.__device_agv_used[DeviceConfig.STATUS_ELEVATOR_LIFTING_UP] != AGVConfig.DONT_USE:
                            response[key].append("Thang máy lên AGV đang sử dụng")

                        if self.__data_pallet_input.get(HandlePalletConfig.EMPTY_INPUT_PALLET_DATA) is None:
                            response[key].append("Chưa có pallet trống đầu vào")

                elif key == "MISSION_M1":
                    if key in self.__running_tasks:
                        response[key].append("ĐANG THỰC HIỆN")
                    else:
                        if self.__status_all_device[DeviceConfig.STATUS_DOCK_M1] != DeviceConfig.DOCK_EMPTY:
                            response[key].append("Dock M1 đang có pallet")
                        if self.__status_all_device[DeviceConfig.STATUS_ELEVATOR_LIFTING_UP] != DeviceConfig.ELEVATOR_LIFTING_READY:
                            response[key].append("Trạng thái thang máy xuống đang bận")

                        if self.__device_agv_used[DeviceConfig.STATUS_DOCK_M1] != AGVConfig.DONT_USE:
                            response[key].append("Dock M1 đang được AGV sử dụng")
                        if self.__device_agv_used[DeviceConfig.STATUS_ELEVATOR_LIFTING_UP] != AGVConfig.DONT_USE:
                            response[key].append("Thang máy xuống AGV đang sử dụng")

                        if self.__data_pallet_input.get(HandlePalletConfig.EMPTY_INPUT_PALLET_DATA) is None:
                            response[key].append("Chưa có pallet trống đầu vào")


                elif key == "MISSION_M2":
                    if key in self.__running_tasks:
                        response[key].append("ĐANG THỰC HIỆN")
                    else:
                        if self.__status_all_device[DeviceConfig.STATUS_DOCK_M2] != DeviceConfig.DOCK_FULL:
                            response[key].append("Dock M2 chưa đầy")
                        if self.__status_all_device[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != DeviceConfig.ELEVATOR_LIFTING_READY:
                            response[key].append("Trạng thái thang máy xuống đang bận")

                        if self.__device_agv_used[DeviceConfig.STATUS_DOCK_M2] != AGVConfig.DONT_USE:
                            response[key].append("Dock M2 đang được AGV sử dụng")
                        if self.__device_agv_used[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != AGVConfig.DONT_USE:
                            response[key].append("Thang máy xuống AGV đang sử dụng")

                elif key == "MISSION_M3":
                    if key in self.__running_tasks:
                        response[key].append("ĐANG THỰC HIỆN")
                    else:
                        if self.__status_all_device[DeviceConfig.STATUS_DOCK_M3] != DeviceConfig.DOCK_FULL:
                            response[key].append("Dock M3 chưa đầy")
                        if self.__status_all_device[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != DeviceConfig.ELEVATOR_LIFTING_READY:
                            response[key].append("Trạng thái thang máy xuống đang bận")

                        if self.__device_agv_used[DeviceConfig.STATUS_DOCK_M3] != AGVConfig.DONT_USE:
                            response[key].append("Dock M3 đang được AGV sử dụng")
                        if self.__device_agv_used[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != AGVConfig.DONT_USE:
                            response[key].append("Thang máy xuống AGV đang sử dụng")

                elif key == "MISSION_M4":
                    if key in self.__running_tasks:
                        response[key].append("ĐANG THỰC HIỆN")
                    else:
                        if self.__status_all_device[DeviceConfig.STATUS_DOCK_M4] != DeviceConfig.DOCK_FULL:
                            response[key].append("Dock M4 chưa đầy")
                        if self.__status_all_device[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != DeviceConfig.ELEVATOR_LIFTING_READY:
                            response[key].append("Trạng thái thang máy xuống đang bận")

                        if self.__device_agv_used[DeviceConfig.STATUS_DOCK_M4] != AGVConfig.DONT_USE:
                            response[key].append("Dock M4 đang được AGV sử dụng")
                        if self.__device_agv_used[DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN] != AGVConfig.DONT_USE:
                            response[key].append("Thang máy xuống AGV đang sử dụng")

                        if self.__status_all_device[DeviceConfig.STATUS_DOCK_REJECT] != DeviceConfig.DOCK_FULL:
                            response[key].append("Dock M4 chưa được gọi trên PDA")

        return response


