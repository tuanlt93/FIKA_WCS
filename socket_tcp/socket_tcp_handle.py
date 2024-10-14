import time
from .socket_tcp_interface import SocketTCP
import socket
from config import CFG_SOCKET
from utils.pattern import Singleton
from utils.logger import Logger

class SocketTCPHandle(SocketTCP, metaclass=Singleton):
    def __init__(self):
        """
            Inherits from SocketTCP to manage sending data via TCP.
        """
        super().__init__(**CFG_SOCKET)
        self.retry_buffer = []  # Buffer to hold messages if needed

    def send_tcp_string(self, message: list):
        """
            Sends a TCP string message to the connected host.
            Args:
                message (list): The list of messages to send.
        """
        formatted_message = "\r\n".join(message) + "\r\n"
        print(formatted_message)
        
        try:
            self.socket_conn.sendall(formatted_message.encode())
            time.sleep(0.02)
        except socket.error as e:
            Logger().error("ERROR SEND DATA MARKEM: " + str(e))

            self.connection_status_tcp = False


    def retry_sending_buffer(self):
        """
            Retry sending all messages stored in the retry buffer.
        """
        for buffered_message in self.retry_buffer:
            try:
                formatted_message = "\r\n".join(buffered_message) + "\r\n"
                self.socket_conn.sendall(formatted_message.encode())
                time.sleep(0.02)
            except socket.error as e:
                Logger().error("RETRY FAILED: " + str(e))
                return  # Stop trying if another error occurs
        # Clear the buffer if successful
        self.retry_buffer.clear()
