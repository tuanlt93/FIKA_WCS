from utils.vntime import VnTimestamp
import requests
from utils.logger import Logger
from config.constants import AGVConfig
from time import sleep
from config import url_gms, url_rms

class MissionBase:
    def __init__(self) -> None:
        self.__url_gms = url_gms
        self.__url_rms = url_rms
        self.instance_ID = None
        self.robot_ID = None
        self.on_pause = False
        
    
    def sendTask(self, workflow_code: str) -> bool:
        """
        response = {
            "header": {
                    "responseId": "9194e002ad324176974ae9438a011ee3",
                    "clientCode": "geekplus",
                    "requestTime": "2020-06-06 18:03:24",
                    "msgType": "InstanceOperationMsg",
                    "code": "0",
                    "msg": "success"
            },
            "body": {
                    "workflowCode": "",
                    "taskCode": "",
                    "instanceId": 8,
                    "robotTaskId": "",
                    "robot": ""
            }
        }
        """
        request_body = {
            "header": {
                "requestId": f'{self.getRequestCode(api_name="sendTask")}',
                "channelId": "client-01",
                "clientCode": "geekplus",
                "requestTime": ""
            },
            "body": {
                "msgType": "WorkflowStartMsg",
                "taskCode": "",
                "workflowCode": f"{workflow_code}",
                "startPoint": "",
                "locationCode": "",
                "containerCategory": "",
                "containerCode": "",
                "nextPoint": "",
                "flowRuleCondition": {
                    "extraParam1": ""
                }
            }
        }
        try:
            res = requests.post(self.__url_gms, json=request_body)
            response = res.json()
            #print(response)
            if response['header']['code'] == '0':
                self.instance_ID = response['body']['instanceId']        
                return True
        except Exception as e:
            Logger().error("SEND TASK ERROR")
        return False
        

    def queryTask(self, location_triger: str, workflow_type :str, robot_direction: str) -> bool:
        """
    
        response = {
            "header": {
                "responseId": "9194e0s4ae9s438sa011ee3",
                "msgType": "WorkflowInstanceListMsg",
                "code": "0",
                "requestTime": null,
                "clientCode": null,
                "msg": "调用成功"
            },
            "body": [
                {
                    "workflowName": "querytask",
                    "workflowCode": "F000058",
                    "instanceId": 177,
                    "taskId": 388,
                    "taskCode": "",
                    "instancePriority": 1,
                    "instanceStatus": 30,
                    "nodeCode": null,
                    "nodeName": null,
                    "locationFrom": "-1",
                    "locationTo": "10000007",
                    "containerCode": null,
                    "robot": "1010",
                    "startTime": "2024-08-30 10:48:14",
                    "taskStatus": 30,
                    "robotStatus": "ARRIVED",
                    "robotError": null
                },
                {
                    "workflowName": "querytask",
                    "workflowCode": "F000058",
                    "instanceId": 177,
                    "taskId": 389,
                    "taskCode": "",
                    "instancePriority": 1,
                    "instanceStatus": 30,
                    "nodeCode": null,
                    "nodeName": null,
                    "locationFrom": "10000007",
                    "locationTo": "20000005",
                    "containerCode": "000104",
                    "robot": "1010",
                    "startTime": "2024-08-30 10:48:14",
                    "taskStatus": 30,
                    "robotStatus": "SHELF_ARRIVED",
                    "robotError": null
                },
                {
                    "workflowName": "querytask",
                    "workflowCode": "F000058",
                    "instanceId": 177,
                    "taskId": 390,
                    "taskCode": "",
                    "instancePriority": 1,
                    "instanceStatus": 30,
                    "nodeCode": null,
                    "nodeName": null,
                    "locationFrom": "20000005",
                    "locationTo": "10000007",
                    "containerCode": "000104",
                    "robot": "1010",
                    "startTime": "2024-08-30 10:48:14",
                    "taskStatus": 30,
                    "robotStatus": "SHELF_ARRIVED",
                    "robotError": null
                },
                {
                    "workflowName": "querytask",
                    "workflowCode": "F000058",
                    "instanceId": 177,
                    "taskId": 391,
                    "taskCode": "",
                    "instancePriority": 1,
                    "instanceStatus": 30,
                    "nodeCode": null,
                    "nodeName": null,
                    "locationFrom": "10000007",
                    "locationTo": "20000008",
                    "containerCode": "000104",
                    "robot": "1010",
                    "startTime": "2024-08-30 10:48:14",
                    "taskStatus": 30,
                    "robotStatus": "SHELF_ARRIVED",
                    "robotError": null
                }
            ]
        }
    
        """

        request_body = {
            "header": {
                "requestId": f'{self.getRequestCode(api_name= "queryRobot" + str(self.instance_ID))}',
                "channelId": "client-01"
            },
            "body": {
                "msgType": "WorkflowInstanceListMsg",
                "workflowName": "",
                "workflowCode": "",
                "instanceId": f"{self.instance_ID}",
                "taskCode": "",
                "instancePriority": "",
                "instanceStatus": "",
                "nodeCode": "",
                "containerCode": "",
                "robot": "",
                "startTime": "",
                "endTime": ""
            }
        }

        try:
            res = requests.post(self.__url_gms, json=request_body)
            response = res.json()
            # print(request_body)
            # print("----------------")
            # print(response)
            robot_status_list = [item['robotStatus'] for item in response['body'] if item['locationTo'] == location_triger and item['robotStatus'] is not None]
            print(robot_status_list)
            if (response['header']['code'] == '0' and 
                robot_status_list):
                
                self.robot_ID = response['body'][0]['robot']
                if workflow_type == AGVConfig.WORKFLOW_INPUT:
                    if robot_status_list[0] == AGVConfig.AGV_SHELF_ARRIVED and robot_direction == AGVConfig.AGV_DIRECTION_ENTER: return True
                    elif len(robot_status_list) > 1 and robot_status_list[1] == AGVConfig.AGV_ARRIVED and robot_direction == AGVConfig.AGV_DIRECTION_EGRESS: return True
                elif workflow_type == AGVConfig.WORKFLOW_OUTPUT:
                    if robot_status_list[0] == AGVConfig.AGV_ARRIVED and robot_direction == AGVConfig.AGV_DIRECTION_ENTER: return True
                    elif len(robot_status_list) > 1 and robot_status_list[1] == AGVConfig.AGV_SHELF_ARRIVED and robot_direction == AGVConfig.AGV_DIRECTION_EGRESS: return True
        except Exception as e:
            Logger().error("QUERY TASK ERROR:", str(e))
        return False
    
    def queryRobot(self) -> bool:
        request_body = {
            "header": {
                "requestId": f'{self.getRequestCode(api_name= "queryRobot" + str(self.instance_ID))}',
                "channelId": "client-01"
            },
            "body": {
                "msgType": "WorkflowInstanceListMsg",
                "workflowName": "",
                "workflowCode": "",
                "instanceId": f"{self.instance_ID}",
                "taskCode": "",
                "instancePriority": "",
                "instanceStatus": "",
                "nodeCode": "",
                "containerCode": "",
                "robot": "",
                "startTime": "",
                "endTime": ""
            }
        }

        try:
            res = requests.post(self.__url_gms, json=request_body)
            response = res.json()
            if (
                response['header']['code'] == '0' and
                response['body'][0]['robot']
            ):
                self.robot_ID = response['body'][0]['robot']
                return True
                
        except Exception as e:
            Logger().error("QUERY TASK ERROR:", str(e))
        return False
    

    def continueRobot(self) -> bool:
        request_body = {
            "header": {
                "requestId": f'{self.getRequestCode(api_name="continueRobot" + str(self.instance_ID))}',
                "channelId": "client-01",
                "clientCode": "geekplus",
                "requestTime": ""   # fomat time 2020-06-06 18:03:24
            },
            "body": {
                "msgType": "InstanceOperationMsg",
                "instruction": "NEXT_STEP",
                "instanceId": f"{self.instance_ID}",
                "containerCode": "",
                "locationCode": "",
                "taskCode": "",
                "nextPoint": "",
                "flowRuleCondition": {
                    "extraParam1": ""
                }
            }
        }     
        try:
            res = requests.post(self.__url_gms, json= request_body)
            response = res.json()
            #print(response)
            if response['header']['code'] == '0':
                return True
        except Exception as e:
            print("CONTINUE ROBOT ERROR", str(e))
        return False
    

    def Pause(self) -> bool:
        request_body = {
            "header": {
                    "requestId": f'{self.getRequestCode(api_name="onPause" + str(self.instance_ID))}',
                    "channelId": "client-01",
                    "clientCode": "geekplus",
                    "requestTime": ""
            },
            "body": {
                    "msgType": "InstanceOperationMsg",
                    "instruction": "STOP",
                    "instanceId": f"{self.instance_ID}",
                    "containerCode": "",
                    "locationCode": "",
                    "taskCode": "",
                    "robotTaskId": "",
                    "robot": ""
            }
        }
        try:
            res = requests.post(self.__url_gms, json= request_body)
            response = res.json()
            #print(response)
            if response['header']['code'] == '0':
                return True
        except Exception as e:
            print("PAUSE ROBOT ERROR", str(e))
        return False
    
    def onPause(self) -> bool:
        while not self.Pause():
           self.on_pause = True
           sleep(1)
    
    def Resume(self) -> bool:
        request_body = {
            "header": {
                    "requestId": f'{self.getRequestCode(api_name="onResume" + str(self.instance_ID) )}',
                    "channelId": "client-01",
                    "clientCode": "geekplus",
                    "requestTime": ""
            },
            "body": {
                    "msgType": "InstanceOperationMsg",
                    "instruction": "ROBOT_RECOVER",
                    "instanceId": f"{self.instance_ID}",
                    "containerCode": "",
                    "locationCode": "",
                    "taskCode": "",
                    "robotTaskId": "",
                    "robot": ""
            }
        }
        try:
            res = requests.post(self.__url_gms, json= request_body)
            response = res.json()
            #print(response)
            if response['header']['code'] == '0':
                return True
        except Exception as e:
            print("RESUME ROBOT ERROR", str(e))
        return False
    
    def onResume(self) -> bool:
        while not self.Resume():
           self.on_pause = False
           sleep(1)
    

    def bindShelf(self, location, shelf_id, angle) -> bool:
        request_body = {
            "header": {
                "requestId": f'{self.getRequestCode(api_name="bindShelf" + str(self.instance_ID))}',
                "channelId": "client-01",
                "clientCode": "geekplus",
                "requestTime": ""
            },
            "body": {
                "msgType": "ContainerOperationMsg",
                "instruction": "ADD_CONTAINER",
                "locationCode": f"{location}",
                "containerCode": f"{shelf_id}",
                "containerCategory": "",
                "containerAngle": f"{angle}"
            }
        }
        try:
            res = requests.post(self.__url_gms, json= request_body)
            response = res.json()
            # print(request_body)
            # print(response)
            if response['header']['code'] == '0':
                return True
        except Exception as e:
            print("BIND SHELF ERROR", str(e))
        return False
    
    
    def unbindSheft(self, shelf_id) -> bool:
        request_body = {
            "header": {
                "requestId": f'{self.getRequestCode(api_name="unbindShelf" + str(self.instance_ID))}',
                "channelId": "client-01",
                "clientCode": "geekplus",
                "requestTime": ""
            },
            "body": {
                "msgType": "ContainerOperationMsg",
                "instruction": "REMOVE_CONTAINER",
                "locationCode": "",
                "containerCode": f"{shelf_id}"
            }
        }
        try:
            res = requests.post(self.__url_gms, json= request_body)
            response = res.json()
            print(response)
            if response['header']['code'] == '0':
                return True
        except Exception as e:
            print("CONTINUE ROBOT ERROR", str(e))
        return False
    

    def undateSheft(self,location, shelf_id) -> bool:
        request_body = {
            "id": "postman_001",
            "msgType": "ParameterInstructionRequestMsg",
            "request": {
                "header": {
                    "requestId": f'{self.getRequestCode(api_name="updateShelf" + str(self.instance_ID))}',
                    "clientCode": "geekCode",
                    "warehouseCode": "geekWarehouseCode",
                    "userId": "admin",
                    "userKey": "111111",
                    "version": "3.3.0",
                    "language": "en_us"
                },
                "body": {
                    "parameterType": "SHELF",
                    "shelfCode": f'{shelf_id}',
                    "locationCellCode": f'{location}'
                }
            }
        }
        try:
            res = requests.post(self.__url_rms, json= request_body)
            response = res.json()
            print(response)
            if response['header']['code'] == '0':
                return True
        except Exception as e:
            print("CONTINUE ROBOT ERROR", str(e))
        return False
    

    def unbindDestination(self, destination: str) -> bool:
        request_body = {
            "header": {
                "requestId": f'{self.getRequestCode(api_name="unbindShelf" + str(self.instance_ID))}',
                "channelId": "client-01",
                "clientCode": "geekplus",
                "requestTime": ""
            },
            "body": {
                "msgType": "ContainerOperationMsg",
                "instruction": "REMOVE_CONTAINER",
                "locationCode": f"{destination}",
                "containerCode": ""
            }
        }
        try:
            res = requests.post(self.__url_gms, json= request_body)
            response = res.json()
            print(response)
            if (
                response['header']['code'] == '0' or
                response['header']['code'] == '4633'
            ):
                return True
        except Exception as e:
            print("UNBIND ROBOT ERROR", str(e))
        return False

    
    def queryDone(self) -> bool:
        request_body = {
            "header": {
                "requestId": f'{self.getRequestCode(api_name="queryDone" + str(self.instance_ID))}',
                "channelId": "11111"
            },
            "body": {
                "msgType": "RobotInfoMsg",
                "robot": f"{self.robot_ID}",
                "robots": [],
                "robotProducts": [
                    "P800TLP"
                ],
                "robotConnectStatus": "",
                "robotTaskStatus": "",
                "robotErrorCode": ""
            }
        }
        try:
            res = requests.post(self.__url_gms, json= request_body)
            response = res.json()
            #print(response)
            if response['header']['code'] == '0':
                for robot_info in response['body']:
                    if robot_info['robot'] == self.robot_ID and robot_info['robotPathMode'] == "IDLE":
                        return True
                        
        except Exception as e:
            print("QUERY INFO ROBOT ERROR", str(e))
        return False
    
    def agv_emergency_stop(self):
        request_body = {
            "header": {
            "requestId": f'{self.getRequestCode(api_name="agv_emergency_stop")}',
            "channelId": "client-01"
            },
            "body": {
            "msgType": "RobotControlMsg",
            "instruction": "FIRE_STOP",
            "areaCodes": []
            }
        }
        try:
            res = requests.post(self.__url_gms, json= request_body)
            response = res.json()
            #print(response)
            if response['header']['code'] == '0':
                return True
                        
        except Exception as e:
            print("EMERGENCY INFO ROBOT ERROR", str(e))
        return False



    def onContinueEnter(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def onContinueEgress(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def onContinueEnterLifting(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def onContinueEgressLifting(self):
        raise NotImplementedError("This method should be overridden by subclasses")


    def onCancel(self):
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def onDone(self):
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def onRcsCallback(self):
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def getRequestCode(self, api_name: str) -> str:
        """
        Generate identical request code for rcs api
        """
        return f"iot-{api_name}-{int(VnTimestamp.now())}"

