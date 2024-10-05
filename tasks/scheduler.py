import schedule
import time
import threading
from apis.DAL import dal_server

class ScheduleThread():
    def __init__(self):
        background_thread = threading.Thread(target=self.__run_schedule)
        background_thread.daemon = True
        background_thread.start()

    def __run_schedule(self):
        print("SCHEDUAL START")
        schedule.every().thursday.at("12:30").do(dal_server.get_token_bearer_backend)
        while True:
            schedule.run_pending()
            time.sleep(30) 