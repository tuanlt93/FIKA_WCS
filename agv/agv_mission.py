from agv.agv_interface import MissionBase
from utils.threadpool import Worker
from config.constants import AGVConfig, DeviceConfig
from db_redis import redis_cache
from PLC import PLC_controller
import time
import json
import threading
from apis.DAL.func_pda import CallApiBackEnd

class MissionHandle(MissionBase):
    def __init__(self, *args, **kwargs) -> None:
        """
        workflow_code: str, location_triger: str
        """
        super().__init__()  # Gọi hàm khởi tạo của lớp cha

        # Kiểm tra các thông tin bắt buộc
        required_keys = [
            'name', 
            'workflow_code', 
            'locationCode_bindCell', 
            'workflow_type',
            'destination',  
            'workflow_type_triger',
            'area',
            'shelf', 
            'angle_shelf', 
        ]

        for key in required_keys:
            if key not in kwargs:
                print(f"Thiếu config {key}")
                return 

        self.__workflow_code = kwargs.get('workflow_code')
        self.__workflow_type = kwargs.get('workflow_type')

        self.__line_curtain_triger = kwargs.get('line_curtain_triger', None)
        self.__workflow_type_triger = kwargs.get('workflow_type_triger')
        
        self.__locationCode_bindCell = kwargs.get('locationCode_bindCell')
        self.__shelf = kwargs.get('shelf')
        self.__angle_shelf = kwargs.get('angle_shelf')
        self.__area = kwargs.get('area')
        self.__destination  = kwargs.get('destination')
        
        self.__mission_name = kwargs.get('name')
        self.instance_ID = kwargs.get('instance_ID', None)
        self.robot_ID = kwargs.get('robot_ID', None)
        self.requirement = kwargs.get('requirement', None)
        
        
        self.key_number_function_passed = 'number_function_passed'
        self.info_task = 'info_task'
            
        self.__cancel = False
        self.__done = False
        self.__continue_enter = False
        self.__continue_egress = False
        self.__continue_enter_lifting =  False
        self.__continue_egress_lifting = False
        self.__redis = redis_cache
        self.__PLC_controller = PLC_controller
        self.__api_backend    = CallApiBackEnd()
        self.__kwargs = kwargs
        self.__number_fc_passed: int = 0
        
        print("START CREATE TASK ROBOT RCS HANDLE")
        
        background_thread = threading.Thread(target=self.main, daemon= True)
        background_thread.start()

        # self.main()

    def waitForCondition(self, condition):
        """Chờ đợi cho đến khi điều kiện được đáp ứng."""
        while not condition():
            time.sleep(0.1)

    def skip_if_below_threshold(self, threshold):
        def decorator(func):
            def wrapper(*args, **kwargs):
                number_function_passed = self.__redis.get("number_function_passed")
                if number_function_passed >= threshold:
                    print(f"Skipping {func.__name__} due to threshold")
                    return
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def performTask(self, task_func, *args, requirement= "Null"):
        """Thực hiện một công việc cho đến khi thành công hoặc bị tạm dừng."""
        while not task_func(*args):
            print(f"Failed to perform {task_func.__name__}, retrying in 5 seconds...")
            time.sleep(5)
        if self.instance_ID:
            self.saveHistory(
                self.__mission_name, 
                self.__kwargs, 
                requirement
            )
        time.sleep(1)

    # @Worker.employ
    def main(self):
        print(f"START TASK {self.__mission_name}")
        

        """
            Demo
        """
        # # Add __mission_name vào group những mision đang chạy
        # self.__redis.sadd(
        #     group= AGVConfig.MISSIONS_RUNNING, 
        #     topic= self.__mission_name
        # )

        # # Khi tạo mission AGV cho dock A1 hoặc A2 -> Tạo pallet pending
        # if (self.__mission_name == "MISSION_A1" or self.__mission_name == "MISSION_A2"):
        #     self.__api_backend.createPallet(self.__mission_name)


        """
            Chương trình chạy chính
        """
        # Set on light
        self.__PLC_controller.set_status_light_button(self.__mission_name)
        
        # Unbind shelf có trên vị trí đến và vị trí lấy shelf
        self.performTask(
            self.unbindDestination, 
            self.__destination
        )
        
        self.performTask(
            self.unbindDestination, 
            self.__locationCode_bindCell
        )

        # Unbind shelf có trên bản đồ
        self.performTask(
            self.unbindSheft, 
            self.__shelf
        )

        # Bind shelf lại vị trí có pallet cần đến lấy
        self.performTask(
            self.bindShelf, 
            self.__locationCode_bindCell, 
            self.__shelf, self.__angle_shelf
        )
        
        # Tạo task cho AGV
        self.performTask(
            self.sendTask, 
            self.__workflow_code
        )
        
        # Add __mission_name vào group những mision đang chạy
        self.__redis.sadd(
            group= AGVConfig.MISSIONS_RUNNING, 
            topic= self.__mission_name
        )

        # Kiểm tra xem có phải dạng Pallet input mang hàng vào không, đặt triger vị trí lấy pallet
        if self.__workflow_type == "PALLET_INPUT":
            # Chờ đến khi dừng tại vị trí lấy pallet đi vào
            self.performTask(
                self.queryTask, 
                self.__workflow_type_triger, 
                AGVConfig.WORKFLOW_OUTPUT, 
                AGVConfig.AGV_DIRECTION_ENTER
            )
           
            # Thông báo đã vào trong dock thang máy đi lên
            self.__PLC_controller.AGV_status_is_in_lifting_up()

            self.performTask(
                self.continueRobot
            )

            # Khi tạo mission AGV cho dock A1 hoặc A2 -> Tạo pallet pending
            if (self.__mission_name == "MISSION_A1" or self.__mission_name == "MISSION_A2"):
                self.__api_backend.createPallet(self.__mission_name)


            # Chờ đến khi dừng tại vị trí lấy pallet đi ra
            self.performTask(
                self.queryTask, 
                self.__workflow_type_triger, 
                AGVConfig.WORKFLOW_OUTPUT, 
                AGVConfig.AGV_DIRECTION_EGRESS
            )
          
            # Thông báo đã đi ra dock thang máy đi lên
            self.__PLC_controller.AGV_status_is_out_lifting_up()

            self.performTask(
                self.continueRobot
            )

        # Kiểm tra xem có phải task cần tắt line curtain không, nếu không thì là task bình thường
        if self.__line_curtain_triger:

            # Query vị trí triger khi nào AGV đến và yêu cầu mở line curtain
            self.performTask(
                self.queryTask, 
                self.__line_curtain_triger, 
                self.__workflow_type, 
                AGVConfig.AGV_DIRECTION_ENTER, 
                requirement = DeviceConfig.LINE_CURTAIN_OPEN
            )

            # Đợi line curtain mở
            self.waitForCondition(lambda: self.__continue_enter)

            # line curtain mở, continue AGV
            self.performTask(
                self.continueRobot, 
                requirement = AGVConfig.AGV_INSIDE
            )

            # Query vị trí triger khi nào AGV ra và yêu cầu đóng line curtain
            self.performTask(
                self.queryTask, 
                self.__line_curtain_triger, 
                self.__workflow_type, 
                AGVConfig.AGV_DIRECTION_EGRESS, 
                requirement = DeviceConfig.LINE_CURTAIN_CLOSE
            )
           
            # Đợi line curtain đóng
            self.waitForCondition(lambda: self.__continue_egress)
           
            # line curtain đóng, continue AGV
            self.performTask(
                self.continueRobot, 
                requirement = DeviceConfig.LINE_CURTAIN_CLOSE
            )

        # Kiểm tra xem có phải dạng Pallet input mang hàng ra không, đặt triger vị trí trả pallet
        if self.__workflow_type == "PALLET_OUTPUT":
            self.performTask(
                self.queryTask, 
                self.__workflow_type_triger, 
                AGVConfig.WORKFLOW_INPUT,  
                AGVConfig.AGV_DIRECTION_ENTER
            )

            # Thông báo đã đi vào dock thang máy đi xuống
            self.__PLC_controller.AGV_status_is_in_lifting_down()
            self.performTask(
                self.continueRobot
            )

            self.performTask(
                self.queryTask, 
                self.__workflow_type_triger, 
                AGVConfig.WORKFLOW_INPUT,  
                AGVConfig.AGV_DIRECTION_EGRESS
            )

            # Thông báo đã đi ra dock thang máy đi xuống
            self.__PLC_controller.AGV_status_is_out_lifting_down()
            self.performTask(
                self.continueRobot
            )

        # Đợi AGV hoàn thành nhiệm vụ
        self.performTask(
            self.queryDone, 
            requirement = DeviceConfig.LINE_CURTAIN_CLOSE
        )

        """
            Hết
        """

        time.sleep(10)
        # Xóa mision đang chạy trong group
        self.__redis.srem(
            group= AGVConfig.MISSIONS_RUNNING, 
            topic= self.__mission_name
        )

        

        self.__PLC_controller.reset_status_light_button(self.__mission_name)
        print("DONE TASK")

    
    def saveHistory(self, redis_hash_name: str, data: dict, requirement) -> None:
        """
        Lưu các giá trị từ dict vào Redis với hset

        :param redis_client: Redis client
        :param redis_hash_name: Tên của hash trong Redis
        :param data: Dữ liệu dict để lưu trữ
        """
        self.__number_fc_passed += 1
        data['number_fc_passed'] = self.__number_fc_passed
        data['instance_ID'] = self.instance_ID
        data['robot_ID'] = self.robot_ID
        data['requirement'] = requirement

        for key, value in data.items():
            self.__redis.hset(
                redis_hash_name, 
                key, 
                value
            )


    def onContinueEnter(self):
        self.__continue_enter =  True
        print(f"----------------onContinueEnter-{self.instance_ID} ---------------")

    def onContinueEgress(self):
        self.__continue_egress = True
        print(f"----------------onContinueEgress-{self.instance_ID}---------------")


    def onContinueEnterLifting(self):
        self.__continue_enter_lifting =  True

    def onContinueEgressLifting(self):
        self.__continue_egress_lifting = True



    def onCancel(self):
        self.__cancel = True

    def onDone(self):
        self.__done = True
       
