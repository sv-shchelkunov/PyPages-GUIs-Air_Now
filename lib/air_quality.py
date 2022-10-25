import sys
import requests
import lib.lat_lon_round_earth as LLRE

class AirQuality():
    __doc__ = """
    #!
    # Args:
    #   zip_code : str
    #       The zip code of the area for which to get air quality data
    #   distance_from: int or str or float
    #       This must be convertable to int, and is measured in miles.
    #   kwargs: typical keyword arguments
    #       'ON_SCREEN' : <any value>
    #           If this is set, the function getAirData(...) will output the data on the screen.
    #       In any case, the data will be saved in self.data_current and self.data_full
    """
    AQI_Numbers = (50, 100, 150, 200, 300, 500)
    AQI_Descriptors = ('Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous')
    AQI_Categories = (1, 2, 3, 4, 5, 6)
    AQI_Colors_Fg = ('#000', '#000', '#ffffff', '#ffffff', '#ffffff', '#ffffff')
    AQI_Colors_Bg = ('#00E400', '#FFFF00', '#FF7E00', '#FF0000', '#8f3f97', '#7E0023')
    def __init__(self, api_key, zip_code, distance_from, **kwargs):
        if 'ON_SCREEN' in kwargs:
            self.ON_SCREEN = True
        else:
            self.ON_SCREEN = False

        self.data_current = None
        self.data_full = None
        self.data_time = None

        self.api_key = api_key
        self.zip_code = zip_code
        self.distance_from = int(distance_from)
        self.requestURL()
        # end of __init__
    #!
    # generates the URL to get current data from https://www.airnowapi.org based on self.zip_code and self.distance_from
    #   The generated URL is stored in self.request_URL
    # Args: none
    # Returns : nothing
    def requestURL(self):
        # self.request_URL = "https://www.airnowapi.org/aq/observation/zipCode/current/"+\
        self.request_URL = "http://localhost:8080/"+\
            "?format=application/json"+\
            f"&zipCode={self.zip_code}"+\
            f"&distance={self.distance_from}"+\
            f"&API_KEY={self.api_key}"
        # end of function
    #!
    # generates the URL to get bounding-box data
    # Args:
    #   date : str
    #       Must be formatted as e.g. 2021-09-29
    #   hour : int or str
    #   BBOX : str
    #       Must be formatted as e.g -73.1281,40.8241,-71.9730,41.6924
    #       See also areaLatLonBox(...) in the module lat_lon_round_earth
    # Returns: request_URL_full :  str
    def requestURLFull(self, date, hour, BBOX):
        date = date.strip()
        # return "https://www.airnowapi.org/aq/data/"+\
        return "http://localhost:8080/"+\
            f"?startDate={date}T{hour}"+\
            f"&endDate={date}T{hour}"+\
            "&parameters=OZONE,PM25,PM10,CO,NO2,SO2"+\
            "&BBOX={}".format(BBOX)+\
            "&dataType=A&format=application/json&verbose=0&monitorType=0&includerawconcentrations=0"+\
            f"&API_KEY={self.api_key}"
        # end of function

    #!
    #
    # Args :
    #   aqi : int
    #       The value of AQI.
    # Returns : tuple
    #   Example : (501, 'Kaboom', 7, '#ffffff', '#000')
    #   The 1st value is aqi (=AQI) itself. The 2nd value is its descriptor (see AQI_Descriptors).
    #   The 3rd value is its category number. The 4rth value is its foreground color.
    #   The 5th value is its background color.
    def getAqiCategory(self, aqi):
        if not (type(aqi) == type(0) or type(aqi) == type(0.0)):
            raise ValueError(f'invalid AQI value {aqi}')

        number_counter = 0
        for each_number in AirQuality.AQI_Numbers:
            if aqi <= each_number:
                return (\
                    aqi,\
                    AirQuality.AQI_Descriptors[number_counter],\
                    AirQuality.AQI_Categories[number_counter],\
                    AirQuality.AQI_Colors_Fg[number_counter],\
                    AirQuality.AQI_Colors_Bg[number_counter])

            number_counter += 1

        return (501, 'Kaboom', 7, '#ffffff', '#000')
        # end of function
    #!
    # processes Air Quality data obtained after the API call using BBOX (bounding-box) style request
    # Args :
    #   data : list
    #       The list with air quality data by a bounding box,
    #       with each member being a dictionary that has elements named 'Parameter' : str, and 'AQI' : int.
    # Returns : dict or int
    #       If a dictionary is returned, each member's key is the name of air quality (OZONE, PM2.5,...).
    #       Each member's value is the average AQI for that air quality.
    #       Example : {'OZONE': 26.714285714285715, 'PM2.5': 10.5, 'PM10': 7.5, 'NO2': 3.0, 'CO': -999.0}
    #       If the provided data : list cannot be procesed, the return value is 0, indicating an error.
    def processAirData(self, data):
        if not isinstance(data, list) or len(data) < 1:
            return 0

        _aqi_names = list()
        _aqi_values = dict()
        _aqi_count = dict()
        for _each in data:
            if not (_each['Parameter'] in _aqi_names):
                _aqi_names.append(_each['Parameter'])
                _aqi_values[_each['Parameter']] = _each['AQI']
                _aqi_count[_each['Parameter']] = 1
            else:
                _aqi_values[_each['Parameter']] = _aqi_values[_each['Parameter']] + _each['AQI']
                _aqi_count[_each['Parameter']] = _aqi_count[_each['Parameter']] + 1

        if len(_aqi_names) < 1:
            return 0

        for _each in _aqi_names:
            _aqi_values[_each] = self.getAqiCategory(_aqi_values[_each] / _aqi_count[_each])

        # print(_aqi_count)
        # print(_aqi_values)
        return _aqi_values
        # end of function
    #!
    # gets Air quality data by executing to API requests: current and BBOX (bonding-box). All data are the most recent.
    #
    #   The current data are for the specified zip code (self.zip_code). See also the function requestURL(...).
    #   Example :
    #       self.data_current = {'O3': (9, 'Good', 1, '#000', '#00E400')}, where 'O3 is for 'OZONE'.
    #
    #   The BBOX data are full data. They repsesent the averaged air quality within the area surrounding the zip code's location.
    #   The area's "radius" is given by self.distance_from.
    #   Example :
    #       self.data_full = {
    #           'OZONE': (16.571428571428573, 'Good', 1, '#000', '#00E400'),
    #           'PM2.5': (8.5, 'Good', 1, '#000', '#00E400'),
    #           'PM10': (8.0, 'Good', 1, '#000', '#00E400'),
    #           'NO2': (1.0, 'Good', 1, '#000', '#00E400'),
    #           'SO2': (0.0, 'Good', 1, '#000', '#00E400'),
    #           'CO': (-999.0, 'Good', 1, '#000', '#00E400')
    #           }
    def getAirData(self, timeout=30):
        try:
            if self.ON_SCREEN:
                print(' ')
                print ("*** Requesting current AirNowAPI data ***")
            # Perform data request (stage 1; current)
            data = requests.get(self.request_URL, timeout=timeout)
            data_status_code = data.status_code
            if self.ON_SCREEN:
                print(f"STATUS CODE: { data_status_code}")
                # print(f"DATA: {data.json()}")
            data_json = data.json()[0]
            self.data_current = {data_json['ParameterName'] : self.getAqiCategory(data_json['AQI'])}
            # Download complete
            self.data_time = data_json['DateObserved'] + ': ' + str(data_json['HourObserved'])
            Latitude = data_json['Latitude']
            Longitude = data_json['Longitude']
            if self.ON_SCREEN:
                Area = data_json['ReportingArea']  + ', ' + data_json['StateCode']
                ParameterName = data_json['ParameterName']
                AQI = data_json['AQI']
                CategoryName = '({}=) {}'.format(data_json['Category']['Number'], data_json['Category']['Name'])

                print(f'Latitude= {Latitude}')
                print(f'Longitude= {Longitude}')
                print(f'Area= {Area}')
                print(f'Time= {self.data_time}')
                print(f'Par= {ParameterName}')
                print(f'AQI= {AQI}')
                print(f'How is it= {CategoryName}')

                print(' ')
                print (f"*** Requesting full AirNowAPI data within {self.distance_from} mile radius ***")
            # Perform data request (stage 2; full)
            p = LLRE.LatLon(Latitude, Longitude)
            box_LatLon = p.areaLatLonBox(LLRE.Dms.MilesToMeters(self.distance_from), BBOX=1)
            # print(box_LatLon)
            request_URL_full = self.requestURLFull(data_json['DateObserved'], data_json['HourObserved'], box_LatLon)
            data = requests.get(request_URL_full, timeout=timeout)
            data_status_code = data.status_code
            self.data_full = self.processAirData(data.json())
            # Download complete
            if self.ON_SCREEN:
                print(f"STATUS CODE: {data_status_code}")
                print(f"Data (full, averaged): {self.data_full}")

        except Exception as e:
            if self.ON_SCREEN:
                print (f"Unable perform AirNowAPI request: {e}")
        # end of function
    #!
    # prints air quality data on screen
    # Args: none.
    # Returns : nothing.
    def printAirData(self):
        print('')
        print(' *** *** *** ')
        print('current data')
        print(self.data_current)

        print('')
        print(' *** *** *** ')
        print('full data')
        print(self.data_full)

# screen centering
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
# end of screen centering
