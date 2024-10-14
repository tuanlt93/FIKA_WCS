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
            host (str): The IP address to connect to (default: "192.168.31.210").
            port (int): The port to connect to (default: 9100).
        """
        self.__host = kwargs.get('host', "192.168.31.210")
        self.__port = kwargs.get('port', 9100)
        self.__timeout = kwargs.get('timeout', 1)
        self.socket_conn = None

        self.__redis_cache = redis_cache
        self.max_reconnect_attempts = kwargs.get('max_reconnect_attempts', 5)

        self.reconnect_delay = 1  # Initial reconnect delay (in seconds)
        self.reconnect_attempts = 0

        self.connection_status_tcp = False

        self.reset_connect()

    def connect(self):
        """Establishes a connection to the specified host and port."""
        try:
            self.socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.socket_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
            self.socket_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)
            self.socket_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

            self.socket_conn.connect((self.__host, self.__port))
            self.__redis_cache.publisher(DeviceConnectStatus.TOPIC_CONNECTION_STATUS_MARKEM, DeviceConnectStatus.CONNECTED)

            self.connection_status_tcp = True
            self.reconnect_delay = 1 
            self.reconnect_attempts = 0

            Logger().info(f"Connected to {self.__host}:{self.__port}")

        except (socket.timeout, socket.error) as e:
            Logger().error(f"Error connecting to {self.__host}:{self.__port} - {e}")
            self.handle_reconnect()

    def handle_reconnect(self):
        """Handles reconnection logic with delay and exponential backoff."""
        self.connection_status_tcp = False
        self.__redis_cache.publisher(DeviceConnectStatus.TOPIC_CONNECTION_STATUS_MARKEM, DeviceConnectStatus.DISCONNECT)

        # Increase the reconnect delay if maximum attempts have not been reached
        if self.reconnect_attempts < self.max_reconnect_attempts:
            Logger().info(f"Attempting to reconnect in {self.reconnect_delay} seconds...")
            time.sleep(self.reconnect_delay)
            self.reconnect_delay = min(self.reconnect_delay * 2, 300)  # Cap delay at 300 seconds
        else:
            Logger().warning("Maximum reconnect attempts exceeded. Will not attempt further reconnects.")

    @Worker.employ
    def reset_connect(self):
        """Continuously checks the PLC connection and manages socket connection accordingly."""
        while True:
            connection_status_plc = self.__redis_cache.hget(
                DeviceConnectStatus.CONNECTION_STATUS_ALL_DEVICE, 
                DeviceConnectStatus.CONNECTION_STATUS_PLC
            )

            if connection_status_plc == DeviceConnectStatus.CONNECTED:
                if not self.connection_status_tcp:
                    self.connect()
            else:
                if self.connection_status_tcp:
                    Logger().info("PLC disconnected, closing socket connection...")
                    self.close()

            time.sleep(5)

    def close(self):
        """Closes the socket connection."""
        if self.socket_conn:
            self.socket_conn.close()
            self.connection_status_tcp = False
            self.socket_conn = None
            Logger().info(f"Closed connection to {self.__host}:{self.__port}")



    def send_tcp_string(self, message: list):
        """
            Sends a TCP string message to the connected host.
            Args:
                message (str): The message to send.
        """
        message = "\r\n".join(message) + "\r\n"
        print(message)
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
            print(message)
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