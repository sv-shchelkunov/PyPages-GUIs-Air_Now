# import requests
#
# AQI_Timeout = 30
# self_request_URL = "http://localhost:8080/"+\
#     "?format=application/json"+\
#     f"&zipCode=20500"+\
#     f"&distance=25"+\
#     f"&API_KEY=shch"
#
# data = requests.get(self_request_URL, timeout=AQI_Timeout)
# data_status_code = data.status_code
#
# print(f"STATUS CODE: { data_status_code}")
# print(f"DATA: {data.json()}")
# print('\n')
# print(data.json()[0])

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lib.air_quality as AQI

air_quality = AQI.AirQuality("", "20500", int("25"), ON_SCREEN=1)
air_quality.getAirData()
air_quality.printAirData()
