# app

import agv
import PLC
import markem_printer
import datamax_printer
import tranfer
import tasks
import time
from apis import FlaskApp


def main():
    app = FlaskApp()
    app.start()

if __name__ == "__main__":
    main()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("Exit")