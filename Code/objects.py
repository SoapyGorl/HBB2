import time

for _ in range(5):
    print(time.time_ns() / 1000000000)
    time.sleep(1)
