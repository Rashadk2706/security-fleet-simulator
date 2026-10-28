import random
import time

while True:
    temp = round(random.uniform(18.0, 26.0), 1)
    air_quality = random.randint(1, 100)
    print(f"temp={temp}C air_quality={air_quality}")
    time.sleep(10)