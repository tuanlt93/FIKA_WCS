from pymodbus.client.sync import ModbusTcpClient
import threading
import time

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
        self.__slave_id = kwargs.get('unit', 1)
        self.__lock = threading.Lock()
        self.__connected = False
        self.__client = None
        self.__connect()

    def __connect(self):
        try:
            self.__client = ModbusTcpClient(
                host=self.__host,
                port=self.__port,
                timeout=self.__timeout
            )
            if self.__client.connect():
                self.__connected = True
                print(f"Successfully connected to PLC at {self.__host}:{self.__port}")
            else:
                # print(f"Failed to connect to PLC at {self.__host}:{self.__port}")
                pass
        except Exception as e:
            # print(f"Error connecting to PLC: {e}")
            self.__connect()

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
        
        if self.__connected:
            with self.__lock:
                try:
                    data = self.__client.read_holding_registers(0, num_register, unit=self.__slave_id)
                    if hasattr(data, 'registers'):
                        return data.registers
                except Exception as e:
                    self.__connected = False
                    print(f"Error reading from PLC: {e}")
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
        if self.__connected:
            with self.__lock:
                try:
                    res = self.__client.write_registers(address, value, unit=self.__slave_id)
                    if res.function_code < 0x80:  # check if the result is not an error
                        return True
                except Exception as e:
                    self.__connected = False
                    print(f"Error sending to PLC: {e}")
        else:
            self.__connect()
        return False

    def close(self):
        self.__client.close()
        self.__connected = False




# print(data)
# community_PLC.close()

# if community_PLC.client.is_socket_open():
#     
# else:
#     print("Connection to PLC is not established. Exiting...")
