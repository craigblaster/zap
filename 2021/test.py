#!/usr/bin/env python3
import time
from datetime import datetime
while True:
    with open("timestamp.txt", "a") as f:
        f.write("\nThe current ts is: " + str(datetime.now()))
        f.close()
    time.sleep(10)
