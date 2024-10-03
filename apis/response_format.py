
class ResponseFomat:
    API_PDA_INPUT = [ 
        "material_code" , "material_name" , "vendor_batch" , "sap_batch" , 
        "expiry_date" , "layer_pallet" , "carton_pallet_qty" , "standard_length" , 
        "standard_width" , "standard_height" , "standard_weight" , "standard_item_carton"
    ]
    API_PDA_PALLET = [ 
        "type"
    ]

    API_CREATE_CARTON_STATE = [ 
        "dws_result", "actual_length", "actual_width", "actual_height", 
        "actual_weight", "actual_item_carton", 
        "link", "description", 
    ]

    API_PDA_CONFIRM_QTY = [ 
        "material_code" , "material_name" , "pallet_code" , "carton_pallet_qty" , 
        "counted" , "actual_carton_pallet"
    ]

    API_CARTON_STATE_INPUT_ERROR = [ 
        "carton_code", "type_result"
    ]

    API_CREATE_INSPECTION= [ 
        "carton_state_id", "status", "visa", "standard_item_carton", "actual_item_carton", 
        "result", "description", "carton_state_code"
    ]


    API_CREATE_CORRECTION = [ 
        "carton_state_id", "status", "standard_item_carton", "actual_item_carton", 
        "result", "description", "carton_state_code"
    ]

    API_PRINT = [ 
        "material_code" , "material_name" , "vendor_batch" , "sap_batch" , 
        "expiry_date" , "carton_code" , "items_carton"
    ]

    API_QUARANTINED = [ 
        "carton_pallet_id" , "actual_item_carton"
    ]

    
    DWS_RESULT = [
        "height" , "width" , "length" , "weight" , 
        "status" , "link"
    ]


    
class BE_TypeCartonError:
    INSPECTION = "inspection"
    CORRECTION = "correction"