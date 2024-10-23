from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Bật CORS cho toàn bộ ứng dụng Flask



@app.route('/cancel/mission/agv', methods=['POST'])
def readData():
    data = request.get_json()
    print(data)
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
                    "instanceId": "8",
                    "robotTaskId": "",
                    "robot": ""
            }
        }
    return jsonify(response)


@app.route('/data/monitor/agv', methods=['GET'])
def demo():
 
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
        "MISSION_M4": ["ĐANG THỰC HIỆN"]
    }
    
    return jsonify(response)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug= True)
