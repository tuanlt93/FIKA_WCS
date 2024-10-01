import socket
import time
from PLC import PLC_controller

class SocketTCP:
    def __init__(self, *args, **kwargs) -> None:
        """
            Initializes a TCP socket connection.
            Args (optional):
                host (str): The IP address to connect to (default: "127.0.0.1").
                port (int): The port to connect to (default: 9100).
        """
        self.__host = kwargs.get('host', "127.0.0.1")
        self.__port = kwargs.get('port', 9100)
        self.__timeout = kwargs.get('timeout', 1.0)
        self.socket_conn = None
        self.__PLC_controller = PLC_controller
        self.connect()

    def connect(self):
        """Establishes a connection to the specified host and port."""
        self.socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket_conn.settimeout(self.__timeout)

        # Bật TCP keep-aliv
        self.socket_conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        self.socket_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)    # Thời gian không hoạt động trước khi gửi gói keep-alive (giây)
        self.socket_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)    # Thời gian giữa các gói keep-alive (giây)
        self.socket_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)      # Số gói keep-alive không nhận được phản hồi trước khi coi là mất kết nối

        try:
            self.socket_conn.connect((self.__host, self.__port))
            print(f"Connected to {self.__host}:{self.__port}")
        except socket.timeout:
            print(f"Connection to {self.__host}:{self.__port} timed out after {self.__timeout} seconds.")
            self.reconnect()
        except socket.error as e:
            print(f"Error connecting to {self.__host}:{self.__port} - {e}")
            self.reconnect()


    def reconnect(self):
        """Attempts to reconnect in case of a connection failure."""
        print("Reconnecting...")
        self.__PLC_controller.status_markem_disconnect()
        self.close()
        while not self.socket_conn:
            self.connect()
            time.sleep(0.5)

    def receive(self, buffer_size=1024):
        """Receive data from the socket with a buffer size."""
        try:
            response = self.socket_conn.recv(buffer_size)  # Receive data from the server
            if response:
                pass
            else:
                print("No response received.")
            return response
        except socket.error as e:
            print(f"Error receiving data: {e}")
            self.reconnect()  
            return None 

    def close(self):
        """Closes the current socket connection."""
        if self.socket_conn:
            self.socket_conn.close()
            self.socket_conn = None
            print("Connection closed.")
