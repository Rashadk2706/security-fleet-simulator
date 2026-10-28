import requests
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEVICE_ID = "camera-01"
DEVICE_TYPE = "camera"
DASHBOARD_URL = "https://10.10.99.10/api/heartbeat"

while True:
    try:
        requests.post(DASHBOARD_URL, json={
            "device_id": DEVICE_ID,
            "type": DEVICE_TYPE,
            "status": "online",
            "timestamp": time.time()
        }, verify=False, timeout=5)
        print("Heartbeat sent.", flush=True)
    except Exception as e:
        print(f"Heartbeat failed: {e}")
    time.sleep(10)