from utils.threadpool import Worker
from agv.agv_mission import MissionHandle
from agv.agv_interface import MissionBase
from time import sleep
from collections import deque
import threading
from config.constants import DeviceConfig, AGVConfig, HandlePalletConfig
from db_redis import redis_cache
from PLC import PLC_controller
from config import DOCK_CONFIGS
from utils.pattern import Singleton
from config.settings import TIME



class ManagerMission(metaclass= Singleton):
    def __init__(self) -> None:
        print("START AGV")
        self.__task_handle_base                 = MissionBase()
        self.__rcs: dict[str,MissionBase]       = {}
        self.__queue_tasks                      = deque()
        self.__redis_cache                      = redis_cache
        self.__PLC_controller                   = PLC_controller
        
        # Khôi phục giá trị của self.__door_close_reset từ Redis
        self.__door_close_reset = {
            'A': self.__redis_cache.get('door_close_reset_A') or False,
            'O': self.__redis_cache.get('door_close_reset_O') or False
        }

        self.__start_background_task()

    def __start_background_task(self):
        background_thread = threading.Thread(target=self.__task_robots)
        background_thread.daemon = True
        background_thread.start()

    def __task_robots(self):

        while True:
            """
            data_task = {
                "workflowCode": "F000057",
                "workflow_type": "PALLET_INPUT",
                "line_curtain_triger": "10000015",
                "area": "A",
                "bindShelf_locationCode": "10000017",
                "shelf": "000102",
                "angle": "0",
                "name": "MISSION_A1",
                "number_fc_passed": "2",
                "instance_ID": "313",
                "robot_ID": "1010",
                "requirement": "OPEN"
            }
            """
            self.__status_all_devices = self.__redis_cache.hgetall(DeviceConfig.STATUS_ALL_DEVICES)
            self.__running_tasks = self.__redis_cache.smembers(AGVConfig.MISSIONS_RUNNING)
            data_pallet_input = self.__redis_cache.hget(
                HandlePalletConfig.PALLET_DATA_MANAGEMENT, 
                HandlePalletConfig.PALLET_INPUT_DATA 
            )

            # print(data_pallet_input)
            
            if self.__handle_emergency_stop():
                print("EMERGENCY STOP")
                sleep(TIME.MANAGER_AGV_SAMPLING_TIME)
                continue

            self.__handle_door_requirements()
            self.__handle_pallet_output()
            if data_pallet_input:
                self.__handle_pallet_input()

            sleep(TIME.MANAGER_AGV_SAMPLING_TIME)


    def __handle_emergency_stop(self):
        try:
            if self.__status_all_devices[DeviceConfig.STATUS_EMERGENCY_STOP] == DeviceConfig.EMERGENCY_ON:
                while not self.__task_handle_base.agv_emergency_stop():
                    sleep(TIME.MANAGER_AGV_SAMPLING_TIME)
                return True
            return False
        except Exception as e:
            print(f"CHECK {e}")
            return False

   

    def __handle_pallet_input(self):
        for dock, config in DOCK_CONFIGS.items():
            if (
                config['workflow_type'] == 'PALLET_INPUT' and 
                f"MISSION_{dock}" not in self.__running_tasks and 
                self.__status_all_devices.get(DeviceConfig.STATUS_ELEVATOR_LIFTING_UP) == DeviceConfig.ELEVATOR_LIFTING_READY and
                len(self.__running_tasks) < AGVConfig.NUMBERS_AGV
            ):

                dock_status = self.__status_all_devices[getattr(DeviceConfig, f'STATUS_DOCK_{dock}')]

                if (dock_status == DeviceConfig.DOCK_EMPTY):
                    
                    self.__rcs[f'MISSION_{dock}'] = MissionHandle(**config)

                    self.__update_device_status(getattr(DeviceConfig, f'STATUS_DOCK_{dock}'), DeviceConfig.DOCK_FULL)
                    self.__update_device_status(DeviceConfig.STATUS_ELEVATOR_LIFTING_UP, DeviceConfig.ELEVATOR_LIFTING_BUSY)
                    break

    def __handle_pallet_output(self):
        for dock, config in DOCK_CONFIGS.items():
            if (
                config['workflow_type'] == 'PALLET_OUTPUT' and 
                f"MISSION_{dock}" not in self.__running_tasks and 
                self.__status_all_devices.get(DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN) == DeviceConfig.ELEVATOR_LIFTING_READY and
                len(self.__running_tasks) < AGVConfig.NUMBERS_AGV
            ):

                dock_status = self.__status_all_devices[getattr(DeviceConfig, f'STATUS_DOCK_{dock}')]
                if dock_status == DeviceConfig.DOCK_FULL:
                    self.__rcs[f'MISSION_{dock}'] = MissionHandle(**config)

                    self.__update_device_status(getattr(DeviceConfig, f'STATUS_DOCK_{dock}'), DeviceConfig.DOCK_EMPTY)
                    self.__update_device_status(DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN, DeviceConfig.ELEVATOR_LIFTING_BUSY)
                    break       

    def __handle_door_requirements(self):
        requirements = {
            'A': [],
            'O': []
        }

        for mission in self.__running_tasks:
            area = self.__redis_cache.hget(topic=mission, key='area')
            if area in requirements:
                requirement = self.__redis_cache.hget(topic=mission, key='requirement')
                requirements[area].append(requirement)
        # print(requirements)
        self.__handle_door('A', requirements['A'], DeviceConfig.STATUS_LINE_CURTAIN_A)
        self.__handle_door('O', requirements['O'], DeviceConfig.STATUS_LINE_CURTAIN_O)


    def __handle_door(self, area, requirements, status_line_curtain):
        requirement_door_open = DeviceConfig.LINE_CURTAIN_OPEN in requirements
        requirement_door_close = DeviceConfig.LINE_CURTAIN_CLOSE in requirements
        all_requirement_door_close = all(req == DeviceConfig.LINE_CURTAIN_CLOSE for req in requirements)
        # Open door request
        if requirement_door_open:
            if self.__status_all_devices[status_line_curtain] == DeviceConfig.LINE_CURTAIN_OPEN:
                self.__allow_agvs_to_enter(DeviceConfig.LINE_CURTAIN_OPEN)
                self.__PLC_controller.reset_request_open_line_curtain(area)  # Reset open request
            elif self.__status_all_devices[status_line_curtain] == DeviceConfig.LINE_CURTAIN_CLOSE:
                self.__PLC_controller.request_open_line_curtain(area)  # Open the door 

        # Close door request
        elif (requirement_door_close and 
              len(requirements) > 1):
            
            if self.__status_all_devices[status_line_curtain] == DeviceConfig.LINE_CURTAIN_OPEN:
                self.__allow_agvs_to_exit(DeviceConfig.LINE_CURTAIN_CLOSE)

        # All requests are to close (but not if there's only one close request)
        elif all_requirement_door_close:
            if self.__status_all_devices[status_line_curtain] == DeviceConfig.LINE_CURTAIN_OPEN:

                self.__allow_agvs_to_exit(DeviceConfig.LINE_CURTAIN_CLOSE)
                self.__PLC_controller.request_close_line_curtain(area)  # Close the door
                self.__door_close_reset[area] = True
                self.__redis_cache.set(f'door_close_reset_{area}', self.__door_close_reset[area])

            elif (self.__status_all_devices[status_line_curtain] == DeviceConfig.LINE_CURTAIN_CLOSE and 
                  self.__door_close_reset.get(area)):
                
                self.__PLC_controller.reset_request_close_line_curtain(area)  # Reset close request
                self.__door_close_reset[area] = False
                self.__redis_cache.set(f'door_close_reset_{area}', self.__door_close_reset[area])

        # No requirements left, reset close bit
        elif (not requirements and 
              self.__status_all_devices[status_line_curtain] == DeviceConfig.LINE_CURTAIN_OPEN):

            self.__PLC_controller.request_close_line_curtain(area)  # Close the door
            self.__door_close_reset[area] = True
            self.__redis_cache.set(f'door_close_reset_{area}', self.__door_close_reset[area])

        # Reset the door close request once the door is closed and no requirements exist
        elif (self.__status_all_devices[status_line_curtain] == DeviceConfig.LINE_CURTAIN_CLOSE and 
              not requirements and 
              self.__door_close_reset.get(area)):
            
            self.__PLC_controller.reset_request_close_line_curtain(area)  # Reset close request
            self.__door_close_reset[area] = False
            self.__redis_cache.set(f'door_close_reset_{area}', self.__door_close_reset[area])




    def __allow_agvs_to_enter(self, requirement):
        try:
            for mission_name in self.__running_tasks:
                mission_data = self.__redis_cache.hgetall(topic=mission_name)
                if mission_data and mission_name in self.__rcs and mission_data['requirement'] == requirement:
                    self.__rcs[mission_name].onContinueEnter()
        except Exception as e:
            print(e)

    def __allow_agvs_to_exit(self, requirement):
        try:
            for mission_name in self.__running_tasks:
                mission_data = self.__redis_cache.hgetall(topic=mission_name)
                if mission_data and mission_name in self.__rcs and mission_data['requirement'] == requirement:
                        self.__rcs[mission_name].onContinueEgress()
        except Exception as e:
            print(e)

    def __update_device_status(self, key, value):
        self.__redis_cache.hset(DeviceConfig.STATUS_ALL_DEVICES, key, value)

