# FIKA

wcs_system/
├── agv/
│   ├── __init__.py
│   ├── agv_manager.py        # Logic điều phối AGV
│   ├── agv_interface.py      # Giao tiếp với hệ thống AGV
│   └── agv_tasks.py          # Các tác vụ liên quan đến AGV
│
├── plc/
│   ├── __init__.py
│   ├── plc_interface.py      # Giao tiếp với PLC
│   └── plc_controller.py     # Xử lý tín hiệu từ PLC
│
├── printer/
│   ├── __init__.py
│   ├── printer_manager.py    # Điều khiển máy in
│   └── printer_interface.py  # Giao tiếp với máy in
│
├── redis/
│   ├── __init__.py
│   ├── redis_client.py       # Tương tác với Redis
│   └── redis_cache.py        # Caching logic
│
├── socket_tcp/
│   ├── __init__.py
│   ├── socket_tcp_handle.py           # Xử lý gửi data
│   └── socket_tcp_interface.py       # Tương tác với socket_tcp
│
├── database/
│   ├── __init__.py
│   ├── db_connection.py      # Quản lý kết nối database
│   ├── models/
│   │   ├── __init__.py
│   │   ├── mission_model.py       # Model dữ liệu người dùng
│   │   ├── setting_model.py      # Model dữ liệu đơn hàng
│   │   └── inventory_model.py  # Model dữ liệu tồn kho
│   └── db_utils.py             # Các hàm tiện ích cho database
│
├── config/
│   ├── __init__.py
│   ├── settings.py           # Cấu hình hệ thống
│   ├── logging_config.py     # Cấu hình logging
│   └── constants.py          # Các hằng số hệ thống
│
├── tasks/
│   ├── __init__.py
│   ├── scheduler.py          # Quản lý và lập lịch các tác vụ
│   ├── task_manager.py       # Xử lý tác vụ chính
│   └── task_processor.py     # Xử lý logic từng tác vụ cụ thể
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py            # Các hàm tiện ích chung
│   ├── validators.py         # Các hàm kiểm tra dữ liệu
│   └── serializers.py        # Chuyển đổi dữ liệu cho các API
|
├── api/
│   ├── __init__.py
│   ├── pda_api.py              # API dành cho PDA
│   ├── routes.py               # Định nghĩa các route cho API
│   ├── auth.py                 # Xác thực người dùng PDA
│   ├── response_format.py      # Định dạng response cho API
│   └── DAL/
│       ├── func_agv.py         # Giao tiếp mongodb tạo mission cho agv
│       └── func_pda.py         # Các fuction lấy dữ liệu cho PDA từ backend
│
├── tests/
│   ├── __init__.py
│   ├── test_agv.py
│   ├── test_plc.py
│   ├── test_printer.py
│   ├── test_database.py
│   └── test_pda_api.py         # Unit test cho API của PDA
│
├── app.py                       # Khởi tạo server, đăng ký route
├── requirements.txt             # Các thư viện cần thiết
├── config.yaml                  # Config IP, port
└── README.md                    # Tài liệu dự án
# FIKA_WCS
