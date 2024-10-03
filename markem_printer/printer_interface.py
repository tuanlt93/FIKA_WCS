from socket_tcp import socket_tcp
from PLC import PLC_controller


class PrintInterface():
    def __init__(self) -> None:
        self.__PLC_controller = PLC_controller
        self.__PLC_controller.status_markem_connect()   
  
    def send_data_print_lable(self, data_print: dict) -> bool:
        messages = []
        if not data_print or data_print is None: 
            # messages.append("!R")
            # messages.append("!C")
            messages.append("!M\"CARTON0\"")
            messages.append("!W1\"\"")
            messages.append("!W2\"\"")
            messages.append("!W3\"\"")
            messages.append("!W4\"\"")
            messages.append("!W5\"\"")
            messages.append("!W6\"\"")
            messages.append("!W7\"\"")
            messages.append("!0D")
            messages.append("!p")
            # messages.append("!P")
            print("NO DATA PRINT")
            
        else:
        
            # messages.append("!R")
            # # messages.append("!C")
            messages.append("!M\"CARTON0\"")
            messages.append(f'!W1\"{data_print["material_code"]}\"')
            messages.append(f'!W1\"{data_print["material_name"]}\"')
            messages.append(f'!W3\"{data_print["vendor_batch"]}\"')
            messages.append(f'!W4\"{data_print["expire_date"]}\"')
            messages.append(f'!W5\"{data_print["quantity"]}\"')
            messages.append(f'!W6\"{data_print["carton_id"]}\"')
            messages.append(f'!W7\"{data_print["sap_batch"]}\"')
            messages.append("!0D")
            messages.append("!p")
            # messages.append("!P")

        socket_tcp.send_tcp_string(messages)
        # response = socket_tcp.receive()
        # if response == b'\r\n':
        #     return True
        # else:
        #     print("Message send to print NOT FEEDBACK")
        #     self.__PLC_controller.status_markem_disconnect()
        #     return False



