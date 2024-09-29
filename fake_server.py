from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Bật CORS cho toàn bộ ứng dụng Flask



@app.route('/', methods=['POST'])
def readData():
 
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=24249)
