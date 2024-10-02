class ConfigAPI:
    name = "admin"
    passwd = "123456"
    # url = "http://4.145.80.147:3100/"
    url = "http://192.168.31.200:3100/"


    url_print_datamax = "http://192.168.31.205:9100/markem/print"
    
    login = "auth/login"
    carton_state = "carton_state"
    carton_qty = "carton_qty"
    carton_error = "carton_error"
    material = "material"
    setting_carton = "setting_carton"
    setting_system = "setting_system"
    setting_call_boxes = "setting_call_boxes"
    setting_call_boxes_info = "setting_call_boxes/dal/info"

    pallet_carton = "carton_pallet/"
    carton_pallet_create = "carton_pallet/dal/create/"
    carton_pallet_start_pallet = "carton_pallet/dal/start_pallet/"
    carton_pallet_change_status = "carton_pallet/dal/change_status/"
    carton_pallet_update_visa = "carton_pallet/dal/update_visa/"
    carton_pallet_code_info = "carton_pallet/dal/info/carton_pallet_code"
    carton_pallet_dws_info = "carton_pallet/dal/dws/"

    carton_state_info = "carton_state/"
    carton_state_printer = "carton_state/dal/printer/"
    carton_state_dws = "carton_state/dal/dws"
    carton_state_confirm_qty = "carton_state/dal/confirm_qty"
    carton_state_get_input = "carton_state/dal/qr_code"
    carton_state_change_status = "carton_state/dal/change_status/"
    carton_state_find_material = "carton_state/dal/find_material/"
    carton_state_code_info = "carton_state/dal/info/carton_code/"

    # Setting system
    setting_system_info = "setting_system/dal/info"

    carton_error_input = "carton_error/dal/create"

    # Carton qty
    carton_qty_info = "carton_qty/dal/info"
    carton_qty_create = "carton_qty/dal/create/"
    carton_qty_update = "carton_qty/dal/update_qty/"

    # PDA history
    pda_history = "pda_history"

    # Quarantined
    quarantined_create = "quarantined/dal"

    # Device
    device_status = "device_status"
    device_status_update = "device_status/dal"

    # Call box
    callboxes_code = "setting_call_boxes/dal/call_boxes_code"

    # Mission history
    mission_history = "mission_history"
    mission_info = "mission_history"
    mission_list = "mission_history/list"
    mission_status = "mission_history/dal"
    mission_history_info = "mission_history/dal/info"
    mission_update_robot = "mission_history/dal/robot"
    mission_update_status = "mission_history/dal/status"
