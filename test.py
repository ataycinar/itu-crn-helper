import time
import sys

try:
    while True:
        current_time = time.strftime("%H:%M:%S")
        # Print clock, '\r' returns cursor to start of the line
        sys.stdout.write("\rCurrent Time: " + current_time)
        sys.stdout.flush()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nClock stopped.")
 