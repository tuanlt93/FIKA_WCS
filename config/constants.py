class AGVConfig:
    # AGV
    NUMBERS_AGV             =  3
    MISSIONS_RUNNING        = "MISSIONS_RUNNING"

    AGV_ARRIVED             = "ARRIVED"
    AGV_SHELF_ARRIVED       = "SHELF_ARRIVED"

    WORKFLOW_INPUT          = "PALLET_INPUT"
    WORKFLOW_OUTPUT         = "PALLET_OUTPUT"

    AGV_DIRECTION_ENTER     = "ROBOT_ENTER"
    AGV_DIRECTION_EGRESS    = "ROBOT_EGRESS"
    
    AGV_INSIDE              = "AGV_INSIDE"
    AGV_OUTSIDE             = "AGV_OUTSIDE"

    ALL_AGV_DEVICE_USED     = "ALL_AGV_DEVICE_USED"
    USED                    = "USED"
    DONT_USE                = "DONT_USE"

class MissionConfig:
    COMPLETE    = "Complete"
    PROCESSING  = "processing"

class STATUS_PALLET_CARTON:
    PENDING = 'pending'
    PROCESSING= 'processing'
    DONE= 'done'

class HandlePalletConfig:
    # Pallet đã và đang làm nhưng chưa xử lý đến pallet tiếp theo
    PALLET_PROCESSED            = "PALLET_PROCESSED"
    NULL_PALLET                 = "NULL_PALLET"
    PALLET_DOCK_A1              = "PALLET_DOCK_A1"
    PALLET_DOCK_A2              = "PALLET_DOCK_A2"


    # Status and quantity for check number cartons
    NUMBER_CARTON_OF_PALLET     = "NUMBER_CARTON_OF_PALLET"
    QUANTITY_FROM_DWS           = "QUANTITY_FROM_DWS"  
    QUANTITY_FROM_PLC           = "QUANTITY_FROM_PLC" 

    # Trạng thái pallet đang xử lý
    STATUS_PALLET_RUNNING       = "STATUS_PALLET_RUNNING"
    
    EXCESS_CARTONS              = "EXCESS_CARTONS"
    MISSIING_CARTONS            = "MISSIING_CARTONS"
    ENOUGH_CARTONS              = "ENOUGH_CARTONS"


    # Group quản lý dữ liệu pallet
    PALLET_DATA_MANAGEMENT      = "PALLET_DATA_MANAGEMENT"

    # List dữ liệu pallet đầu vào 
    INPUT_PALLET_DATA      = "INPUT_PALLET_DATA"

    # List dữ liệu pallet đầu vào vị trí A1 
    INPUT_PALLET_A1_DATA   = "INPUT_PALLET_A1_DATA"

    # List dữ liệu pallet đầu vào vị trí A2 
    INPUT_PALLET_A2_DATA   = "INPUT_PALLET_A2_DATA"

    # List dữ liệu pallet đang chạy
    LIST_PALLET_RUNNING    = "LIST_PALLET_RUNNING"

    # List dữ liệu pallet rỗng đầu vào 
    EMPTY_INPUT_PALLET_DATA     = "EMPTY_INPUT_PALLET_DATA"

    LIST_NUMBER_CARTON_START_NEW_PALLET = [0,1,2,3]



class HandleCartonConfig:

    # Kích thước các thùng cacton
    MEASUREMENR_CARTON  = "MEASUREMENR_CARTON"

    # Trạng thái các thùng carton
    OK = "OK"
    OK_CHECK = "OK-CHECK"

class SETTING_SYSTEM:
    TOPIC_SETTING_SYSTEM    = "TOPIC_SETTING_SYSTEM"
    DWS_WEIGHT              = "DWS_WEIGHT"
    DWS_SIZE                = "DWS_SIZE"
    INTERVAL                = "INTERVAL"

class ERROR_DWS:
    UNDER_WEIGHT = "Lỗi thiếu cân"
    OVER_WEIGHT = "Lỗi thừa cân"
    
    WRONG_SIZE = "Lỗi sai kích thước"
    
    WRONG_SIZE_UNDER_WEIGHT = "Lỗi sai kích thước – thiếu cân"
    WRONG_SIZE_OVER_WEIGHT = "Lỗi sai kích thước – thừa cân"


class DWSConfig:
    TOPIC_TOPIC_ERROR_NO_WEIGHT     = "TOPIC_TOPIC_ERROR_NO_WEIGHT"

    CARTON_NO_WEIGHT                = "CARTON_NO_WEIGHT"



class SorterConfig:
    # Sortting location corection 
    TOPIC_STT_CARTON_AFTER_INSPECTION   = "TOPIC_STT_CARTON_AFTER_INSPECTION"


class MarkemConfig:
    # Topic notify print markem
    TOPIC_NOTIFY_SEND_DATA_PRINT        = "TOPIC_NOTIFY_SEND_DATA_PRINT"
    MESSAGE_NOTIFY_PRINT                = "MESSAGE_NOTIFY_PRINT"
    DATA_CARTON_LABLE_PRINT             = "DATA_CARTON_LABLE_PRINT"

    # Topic pubsub redis thông báo barcode không đọc được tem in ra
    TOPIC_MARKEM_PRINTER_RESULTS        = "TOPIC_MARKEM_PRINTER_RESULTS"
    MESSAGE_PRINTED_WRONG               = "MESSAGE_PRINTED_WRONG"

    DATA_PRINT_SHOW = "DATA_PRINT_SHOW"

     # Thông báo đã in tem dừng máy in
    MESSAGE_NOTIFY_PAUSE_PRINT  = "MESSAGE_NOTIFY_PAUSE_PRINT"


class DeviceConfig:
    # ALL device for create mission
    STATUS_ALL_DEVICES      = "STATUS_ALL_DEVICES"

    STATUS_DOCK_A1          = "STATUS_DOCK_A1"
    STATUS_DOCK_A2          = "STATUS_DOCK_A2"
    STATUS_DOCK_A3          = "STATUS_DOCK_A3"

    STATUS_DOCK_O1          = "STATUS_DOCK_O1"
    STATUS_DOCK_O2          = "STATUS_DOCK_O2"
    STATUS_DOCK_O3          = "STATUS_DOCK_O3"

    STATUS_DOCK_M1          = "STATUS_DOCK_M1"
    STATUS_DOCK_M2          = "STATUS_DOCK_M2"
    STATUS_DOCK_M3          = "STATUS_DOCK_M3"
    STATUS_DOCK_M4          = "STATUS_DOCK_M4"
    STATUS_DOCK_REJECT      = "STATUS_DOCK_REJECT"

    DOCK_EMPTY              = "EMPTY"
    DOCK_PALLET             = "DOCK_PALLET"
    DOCK_FULL               = "FULL"
    DOCK_PROCESSING         = "DOCK_PROCESSING"

    # Trạng thái line curtain

    STATUS_LINE_CURTAIN_O   = "STATUS_LINE_CURTAIN_O"
    STATUS_LINE_CURTAIN_A   = "STATUS_LINE_CURTAIN_A"

    LINE_CURTAIN_OPEN       = "OPEN"
    LINE_CURTAIN_CLOSE      = "CLOSE"

    RESET_OPEN_LINE_CURTAIN_A    = "RESET_OPEN_LINE_CURTAIN_A"
    RESET_CLOSE_LINE_CURTAIN_A   = "RESET_CLOSE_LINE_CURTAIN_A"

    RESET_OPEN_LINE_CURTAIN_O    = "RESET_OPEN_LINE_CURTAIN_O"
    RESET_CLOSE_LINE_CURTAIN_O   = "RESET_CLOSE_LINE_CURTAIN_O"

    #Emergency stop
    STATUS_EMERGENCY_STOP   = "STATUS_EMERGENCY_STOP"
    EMERGENCY_ON            = "EMERGENCY_ON"    
    EMERGENCY_OFF           = "EMERGENCY_OFF"

    #Khu vực thang máy
    STATUS_ELEVATOR_AREA        = "STATUS_ELEVATOR_AREA"
    ALL_ELEVATOR_AREA_AUTO      = "ALL_ELEVATOR_AREA_AUTO"
    ELEVATOR_UP_AREA_MANUAL     = "ELEVATOR_UP_AREA_MANUAL"
    ELEVATOR_DOWN_AREA_MANUAL   = "ELEVATOR_DOWN_AREA_MANUAL"  
    ALL_ELEVATOR_AREA_MANUAL    = "ALL_ELEVATOR_AREA_MANUAL"

    # Trạng thái 2 tele scope vị trí thang máy lên và xuống
    STATUS_ELEVATOR_LIFTING_UP      = "STATUS_ELEVATOR_LIFTING_UP"
    STATUS_ELEVATOR_LIFTING_DOWN    = "STATUS_ELEVATOR_LIFTING_DOWN"
    ELEVATOR_LIFTING_BUSY           = "ELEVATOR_LIFTING_BUSY"
    ELEVATOR_LIFTING_READY          = "ELEVATOR_LIFTING_READY"

    # Xác nhận đã lấy hàng cặp kè về vị trí gốc
    STATUS_NOTIFY_RETURN_CARTONS    = "STATUS_NOTIFY_RETURN_CARTONS"
    WAIT_ACCEPT = "WAIT_ACCEPT"
    ACEPTED = "ACEPTED"

    # Tín hiệu báo không in được tem, không đọc được qr code vị trí sorter
    MARKEM_PRINTER_RESULTS  = "MARKEM_PRINTER_RESULTS"
    PRINT_CORRECTLY         = "PRINT_CORRECTLY"
    PRINTED_WRONG           = "PRINTED_WRONG"

class RegisterConfig:
    # Chỉ đọc giá trị các thanh ghi và map với trạng thái tương ứng quy ước
    REGISTER_CONFIG = {
        10: [DeviceConfig.RESET_OPEN_LINE_CURTAIN_A, False, True],
        11: [DeviceConfig.RESET_CLOSE_LINE_CURTAIN_A, False, True],
        13: [DeviceConfig.RESET_OPEN_LINE_CURTAIN_O, False, True],
        14: [DeviceConfig.RESET_CLOSE_LINE_CURTAIN_O, False, True],

        12: [DeviceConfig.STATUS_LINE_CURTAIN_A, DeviceConfig.LINE_CURTAIN_CLOSE, DeviceConfig.LINE_CURTAIN_OPEN],
        15: [DeviceConfig.STATUS_LINE_CURTAIN_O, DeviceConfig.LINE_CURTAIN_CLOSE, DeviceConfig.LINE_CURTAIN_OPEN],
        16: [DeviceConfig.STATUS_DOCK_A1, DeviceConfig.DOCK_EMPTY, DeviceConfig.DOCK_PALLET, DeviceConfig.DOCK_PROCESSING],
        17: [DeviceConfig.STATUS_DOCK_A2, DeviceConfig.DOCK_EMPTY, DeviceConfig.DOCK_PALLET, DeviceConfig.DOCK_PROCESSING],
        18: [DeviceConfig.STATUS_DOCK_A3, DeviceConfig.DOCK_EMPTY, DeviceConfig.DOCK_PALLET, DeviceConfig.DOCK_FULL],

        20: [HandlePalletConfig.STATUS_PALLET_RUNNING, HandlePalletConfig.ENOUGH_CARTONS, HandlePalletConfig.MISSIING_CARTONS, HandlePalletConfig.EXCESS_CARTONS],
        23: [HandlePalletConfig.PALLET_PROCESSED, HandlePalletConfig.NULL_PALLET, HandlePalletConfig.PALLET_DOCK_A1, HandlePalletConfig.PALLET_DOCK_A2],

        24: [DeviceConfig.STATUS_NOTIFY_RETURN_CARTONS, DeviceConfig.WAIT_ACCEPT, DeviceConfig.ACEPTED],

        26: [DeviceConfig.STATUS_DOCK_O1, DeviceConfig.DOCK_EMPTY, DeviceConfig.DOCK_PALLET, DeviceConfig.DOCK_FULL],
        27: [DeviceConfig.STATUS_DOCK_O2, DeviceConfig.DOCK_EMPTY, DeviceConfig.DOCK_PALLET, DeviceConfig.DOCK_FULL],
        28: [DeviceConfig.STATUS_DOCK_O3, DeviceConfig.DOCK_EMPTY, DeviceConfig.DOCK_FULL],

        30: [DeviceConfig.STATUS_DOCK_M1, DeviceConfig.DOCK_EMPTY, DeviceConfig.DOCK_FULL],
        31: [DeviceConfig.STATUS_DOCK_M2, DeviceConfig.DOCK_EMPTY, DeviceConfig.DOCK_FULL],
        32: [DeviceConfig.STATUS_DOCK_M3, DeviceConfig.DOCK_EMPTY, DeviceConfig.DOCK_FULL],
        33: [DeviceConfig.STATUS_DOCK_M4, DeviceConfig.DOCK_EMPTY, DeviceConfig.DOCK_FULL],

        34: [DeviceConfig.MARKEM_PRINTER_RESULTS, DeviceConfig.PRINT_CORRECTLY, DeviceConfig.PRINTED_WRONG],

        92: [DeviceConfig.STATUS_ELEVATOR_AREA, DeviceConfig.ALL_ELEVATOR_AREA_AUTO ,DeviceConfig.ELEVATOR_UP_AREA_MANUAL, DeviceConfig.ELEVATOR_DOWN_AREA_MANUAL, DeviceConfig.ALL_ELEVATOR_AREA_MANUAL],

        95: [DeviceConfig.STATUS_ELEVATOR_LIFTING_UP, DeviceConfig.ELEVATOR_LIFTING_BUSY, DeviceConfig.ELEVATOR_LIFTING_READY],
        96: [DeviceConfig.STATUS_ELEVATOR_LIFTING_DOWN, DeviceConfig.ELEVATOR_LIFTING_BUSY, DeviceConfig.ELEVATOR_LIFTING_READY],
        97: [DeviceConfig.STATUS_EMERGENCY_STOP, DeviceConfig.EMERGENCY_OFF, DeviceConfig.EMERGENCY_ON],

    }




class DeviceConnectStatus:
    CONNECTION_STATUS_ALL_DEVICE    = "CONNECTION_STATUS_ALL_DEVICE"

    CONNECTION_STATUS_PLC           = "CONNECTION_STATUS_PLC"
    CONNECTION_STATUS_MARKEM        = "CONNECTION_STATUS_MARKEM"

    TOPIC_CONNECTION_STATUS_MARKEM  = "TOPIC_CONNECTION_STATUS_MARKEM"
    
    CONNECTED                       = "CONNECTED"
    DISCONNECT                      = "DISCONNECT"
