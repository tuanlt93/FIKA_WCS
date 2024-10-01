# app

import agv
import PLC
import markem_printer
# import sorter
import time
from apis import FlaskApp



if __name__ == "__main__":
    app = FlaskApp()
    app.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("Exit")