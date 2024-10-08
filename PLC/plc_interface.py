from pymodbus.client.sync import ModbusTcpClient
import threading
import time
from config.constants import DeviceConnectStatus
from db_redis import redis_cache
from utils.logger import Logger

class PLCSInterface():
    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the connection parameters for the PLC station.

        Args:
            host: IP address of the PLC (default: "127.0.0.1")
            port: Modbus TCP port (default: 502)
            timeout: Timeout for Modbus operations (default: 1 second)
            unit: Modbus slave ID (default: 1)
        """

        self.__host = kwargs.get('host', "192.168.31.3")
        self.__port = kwargs.get('port', 502)
        self.__timeout = kwargs.get('timeout', 1)
        self.__slave_id = kwargs.get('unit', 16)

        self.__lock     = threading.Lock()
        self.__redis_cache = redis_cache

        self.connected = False
        self.__client = None
        self.__error_count = 0
        self.__max_backoff = 60  # Giới hạn thời gian backoff tối đa là 60 giây
        self.__min_backoff = 0.1  # Thời gian chờ tối thiểu là 0.1 giây
        self.__backoff_time = self.__min_backoff
        self.__connect()
    

    def __connect(self):
        try:
            self.__client = ModbusTcpClient(
                host=self.__host,
                port=self.__port,
                timeout=self.__timeout
            )
            if self.__client.connect():
                self.connected = True
                self.__error_count = 0  # Reset số lỗi
                self.__backoff_time = self.__min_backoff  # Reset thời gian backoff

                self.__redis_cache.hset(
                    DeviceConnectStatus.CONNECTION_STATUS_ALL_DEVICE, 
                    DeviceConnectStatus.CONNECTION_STATUS_PLC, 
                    DeviceConnectStatus.CONNECTED
                )

                Logger().info(f"Successfully connected to PLC at {self.__host}:{self.__port}")
            else:
                Logger().error("Failed to connect to PLC")
        except Exception as e:
            self.__handle_connection_error(e)


    def __handle_connection_error(self, error):
        self.connected = False
        self.__error_count += 1
        Logger().debug(f"Error: {error}, Error count: {self.__error_count}")

        # Tăng thời gian backoff theo cấp số nhân nhưng không vượt quá giới hạn
        self.__backoff_time = min(self.__backoff_time * 2, self.__max_backoff)
        Logger().debug(f"Backing off for {self.__backoff_time} seconds before retrying.")
        time.sleep(self.__backoff_time)


    def read_data(self, num_register: int) -> list:
        """
            0x01: Read Coils
            0x03: Read Holding Registers
            0x05: Write Single Coil
            0x06: Write Single Register
            0x10: Write Multiple Registers
            0x81: Illegal Function
            0x82: Illegal Data Address
            0x83: Illegal Data Value
            0x84: Slave Device Failure
        """
        
        if self.connected:
            with self.__lock:
                try:
                    data = self.__client.read_holding_registers(0, num_register, unit=self.__slave_id)
                    if hasattr(data, 'registers'):
                        return data.registers
                except Exception as e:
                    self.connected = False

                    self.__redis_cache.hset(
                        DeviceConnectStatus.CONNECTION_STATUS_ALL_DEVICE, 
                        DeviceConnectStatus.CONNECTION_STATUS_PLC, 
                        DeviceConnectStatus.DISCONNECT
                    )
                    
                    Logger().error(f"Error reading from PLC: {e}")
        else:
            self.__connect()
        return [None]

    def write_data(self, address: int, value: list[int]) -> bool:
        """
            0x01: Read Coils
            0x03: Read Holding Registers
            0x05: Write Single Coil
            0x06: Write Single Register
            0x10: Write Multiple Registers
            0x81: Illegal Function
            0x82: Illegal Data Address
            0x83: Illegal Data Value
            0x84: Slave Device Failure
        """
        if self.connected:
            with self.__lock:
                try:
                    res = self.__client.write_registers(address, value, unit=self.__slave_id)
                    if res.function_code < 0x80:  # check if the result is not an error
                        return True
                except Exception as e:
                    self.connected = False
                    
                    redis_cache.hset(
                        DeviceConnectStatus.CONNECTION_STATUS_ALL_DEVICE, 
                        DeviceConnectStatus.CONNECTION_STATUS_PLC, 
                        DeviceConnectStatus.DISCONNECT
                    )
                    Logger().error(f"Error sending from PLC: {e}")
        else:
            self.__connect()
        return False

    def close(self):
        self.__client.close()
        self.connected = False




# print(data)
# community_PLC.close()

# if community_PLC.client.is_socket_open():
#     
# else:
#     print("Connection to PLC is not established. Exiting...")
