import time
from .socket_tcp_interface import SocketTCP
import socket
from config import CFG_SOCKET
from utils.pattern import Singleton
from utils.logger import Logger

class SocketTCPHandle(SocketTCP, metaclass= Singleton):
    def __init__(self):
        """
            Inherits from SocketTCP to manage sending data via TCP.
        """
        super().__init__(**CFG_SOCKET)

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
            Logger().error("ERROR SEND DATA MARKEM" + str(e))
            self.connect()
            self.send_tcp_string([])
            self.send_tcp_string(message)  # Retry sending the message after reconnecting
