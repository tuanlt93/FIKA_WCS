import socket
import time
from db_redis import redis_cache
from config.constants import DeviceConnectStatus
from utils.threadpool import Worker
from utils.logger import Logger

class SocketTCP:
    def __init__(self, *args, **kwargs) -> None:
        """
            Initializes a TCP socket connection.
            Args (optional):
                host (str): The IP address to connect to (default: "127.0.0.1").
                port (int): The port to connect to (default: 9100).
        """
        self.__host = kwargs.get('host', "192.168.31.210")
        self.__port = kwargs.get('port', 9100)
        self.__timeout = kwargs.get('timeout', 1)
        self.socket_conn = None

        self.__redis_cache = redis_cache

        self.max_reconnect_attempts = kwargs.get('max_reconnect_attempts', 5)
        self.reconnect_attempts = 0
        self.reconnect_delay = 1  # Initial reconnect delay (in seconds)
        
        self.connection_status_plc = DeviceConnectStatus.DISCONNECT
        self.connection_status_tcp = False
        
        self.connect()
        # self.receive()

    def connect(self):
        """Establishes a connection to the specified host and port."""
        self.socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket_conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.socket_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)    # Idle time before keep-alive (seconds)
        self.socket_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)    # Interval between keep-alive packets (seconds)
        self.socket_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)      # Max number of failed keep-alive probes before disconnect

        while True:
            self.connection_status_plc = self.__redis_cache.hget(
                DeviceConnectStatus.CONNECTION_STATUS_ALL_DEVICE, 
                DeviceConnectStatus.CONNECTION_STATUS_PLC
            )
            if self.connection_status_plc == DeviceConnectStatus.CONNECTED:
                break
            time.sleep(5)
        
        while not self.connection_status_tcp:
            try:
                self.socket_conn.connect((self.__host, self.__port))
                
                self.__redis_cache.publisher(
                    DeviceConnectStatus.TOPIC_CONNECTION_STATUS_MARKEM, 
                    DeviceConnectStatus.CONNECTED
                )

                self.connection_status_tcp = True
                self.reconnect_attempts = 0  # Reset attempts on successful connection
                self.reconnect_delay = 1  # Reset delay on success
                Logger().info(f"Connected to {self.__host}:{self.__port}")
                break  # Break loop once connection is established

            except socket.timeout:
                Logger().info(f"Connection to {self.__host}:{self.__port} timed out after {self.__timeout} seconds.")
                self.handle_reconnect()

            except socket.error as e:
                Logger().error(f"Error connecting to {self.__host}:{self.__port} - {e}")
                self.handle_reconnect()

            time.sleep(self.reconnect_delay)  # Wait before attempting to reconnect


    def handle_reconnect(self):
        """Handles reconnection logic with delay and exponential backoff."""
        self.reconnect_attempts += 1
        self.connection_status_tcp =False

        if self.reconnect_attempts <= self.max_reconnect_attempts:
            Logger().info(f"Reconnecting... Attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        else:
            Logger().info(f"Reconnecting... Attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")

        self.__redis_cache.publisher(
                DeviceConnectStatus.TOPIC_CONNECTION_STATUS_MARKEM, 
                DeviceConnectStatus.DISCONNECT
            )

        if self.reconnect_attempts > self.max_reconnect_attempts:
            # After exceeding max attempts, use an exponential backoff strategy
            self.reconnect_delay = min(self.reconnect_delay * 2, 300)  # Cap delay at 900 seconds (15 minutes)

    @Worker.employ
    def reset_connect(self):
        while True:
            self.connection_status_plc = self.__redis_cache.hget(
                DeviceConnectStatus.CONNECTION_STATUS_ALL_DEVICE, 
                DeviceConnectStatus.CONNECTION_STATUS_PLC
            )
            if (self.connection_status_plc == DeviceConnectStatus.DISCONNECT and
                self.reconnect_attempts == 0
            ):
                self.connect()
            time.sleep(5)

    def close(self):
        """Closes the socket connection."""
        if self.socket_conn:
            self.socket_conn.close()
            self.connection_status_tcp =False
            self.socket_conn = None
            Logger().info(f"Closed connection to {self.__host}:{self.__port}")


    def send_tcp_string(self, message: list):
        """
            Sends a TCP string message to the connected host.
            Args:
                message (str): The message to send.
        """
        message = "\r\n".join(message) + "\r\n"
        try:
            self.socket_conn.sendall(message.encode())
            time.sleep(0.02)

        except socket.error as e:
            Logger().error(f"Error sending message MARKEM: {e}")
            self.connection_status_tcp = False

            self.__redis_cache.publisher(
                DeviceConnectStatus.TOPIC_CONNECTION_STATUS_MARKEM, 
                DeviceConnectStatus.DISCONNECT
            )
            self.connect()
            # self.send_tcp_string([])
            self.send_tcp_string(message)  # Retry sending the message after reconnecting



    @Worker.employ
    def receive(self, buffer_size=1024):
            """Receive data from the socket with a buffer size."""
            try:
                response = self.socket_conn.recv(buffer_size)  # Receive data from the server
                if response:
                    print(f"response received: {response}")
                else:
                    print("No response received.")
            except socket.error as e:
                print(f"Error receiving data: {e}")
                self.connect()  
                return None 