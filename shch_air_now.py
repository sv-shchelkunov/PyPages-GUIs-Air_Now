import lib.air_quality as AQI
from lib.shch_air_now_lib import ApiKeyChange as AKC

import getpass
import os
import json
from PIL import ImageTk as pil_image_tk
from PIL import Image as pil_image
import tkinter as tk
from tkinter import messagebox as tk_messagebox

DEBUG = False
GET_AIR_DATA = True
AIR_DATA_TIMEOUT = 60
HOME_DIR = None
CONFIG_FOLDER = 'shch_air_now_cfg'
ICO_FILE = None
CURRENT_USER = None
API_KEY = None
ZIP_CODE = None
DISTANCE_FROM = None
HAS_AREA_CHANGED = False
WIDGET_FONT_SIZES = (6, 8, 10, 12, 14, 16, 18, 22, 24, 28, 32, 36) # predefined scales for buttons, and labels
WIDGET_FONT_SIZE_INDEX = 7

#!
# returns the font size
# Args:
#   kwargs: typical keyword arguments.
#       'primero' : <any value>
#           Sets the returned value to self.WIDGET_FONT_SIZES[self.WIDGET_FONT_SIZE_INDEX]
#       'segundo': <any value>
#           Sets the returned value to 12/14 of 'primero'
#       'tercero': <any value>
#           Sets the returned value to 11/14 of 'primero'
#       'cuarto': <any value>
#           Sets the returned value to 10/14 of 'primero'
#       'quinto': <any value>
#           Sets the returned value to 9/14 of 'primero'
#       'sexto': <any value>
#           Sets the returned value to 8/14 of 'primero'
# Returns: font_size : int
#   If no kwargs are given it will default to 'primero'.
def fnc_font(**kwargs):
    global WIDGET_FONT_SIZES, WIDGET_FONT_SIZE_INDEX
    if WIDGET_FONT_SIZE_INDEX < 0:
        WIDGET_FONT_SIZE_INDEX = 0
    if WIDGET_FONT_SIZE_INDEX > len(WIDGET_FONT_SIZES) - 1:
        WIDGET_FONT_SIZE_INDEX = len(WIDGET_FONT_SIZES) - 1

    if 'primero' in kwargs:
        # print(WIDGET_FONT_SIZES[WIDGET_FONT_SIZE_INDEX])
        return WIDGET_FONT_SIZES[WIDGET_FONT_SIZE_INDEX]


    _coeff = 1.0

    if 'segundo' in kwargs:
        _coeff = 13/14.
        # print(WIDGET_FONT_SIZES[WIDGET_FONT_SIZE_INDEX])
    if 'tercero' in kwargs:
        _coeff = 11/14.
    if 'cuarto' in kwargs:
        _coeff = 10/14.
    if 'quinto' in kwargs:
        _coeff = 9/14.
    if 'sexto' in kwargs:
        _coeff = 8/14.

    return int(_coeff* WIDGET_FONT_SIZES[WIDGET_FONT_SIZE_INDEX])
#!
# changes button sizes on the display.
# Args:
#   tk_window : tkinter window created via the tk.Tk(...) method.
#   index_increment : int
#       The amount by which to increment or decrement the (current) size index.
#       If the new index is < 0, it is set to 0. If the new index is larger than the last
#       index of self.WIDGET_FONT_SIZES, it is set to the last index of self.WIDGET_FONT_SIZES
# Returns: nothing.
def fnc_regDisplay(tk_window, index_increment, **kwargs):
    global AIR_DATA, HAS_AREA_CHANGED
    global WIDGET_FONT_SIZE_INDEX
    WIDGET_FONT_SIZE_INDEX += index_increment
    # the index above is normalized in fnc_font(...)

    api_key, zip_code, distance_from = fnc_paintStart(tk_window, paint_again=1, menu = kwargs['menu'])
    if HAS_AREA_CHANGED:
        AIR_DATA = fnc_renewAirData(api_key, zip_code, distance_from)
        HAS_AREA_CHANGED = False

    fnc_paint(tk_window, AIR_DATA)
    # end of function

#!
# starts to paint. It creates frames, and fills the top frame with labels, entry boxes, and buttons.
#   It also creates three global variables:
#   IS_CLOSING : bool, FRAMES : dict, and RENEWABLE_COMPONENTS : dict.
# Args:
#   tk_window : tkinter window created via the tk.Tk(...) method.
#   kwargs: usual keyword args.
#       'paint_again' :  <any value>
#           If set, all frames will be erased, and then build again.
#           This is to be used when changing fonts' sizes, or for similar operations.
# Returns : tuple
#   It is (zip_code : str, distance_from : str) as in the tuple
#   (ENTRY_COMPONENTS['tk_entry_zip_code'].get(), ENTRY_COMPONENTS['tk_entry_distance_from'].get())
def fnc_paintStart(tk_window, **kwargs):
    global HOME_DIR, CONFIG_FOLDER, ICO_FILE
    global API_KEY, ZIP_CODE, DISTANCE_FROM, HAS_AREA_CHANGED
    global IS_CLOSING, MENUS, FRAMES, RENEWABLE_COMPONENTS, ENTRY_COMPONENTS

    _ico_folder_path = os.path.join(HOME_DIR, CONFIG_FOLDER)
    _ico_file_path = os.path.join(_ico_folder_path, ICO_FILE)

    if 'paint_again' in kwargs:
        _zip_code = ENTRY_COMPONENTS['tk_entry_zip_code'].get()
        HAS_AREA_CHANGED = (_zip_code != ZIP_CODE)
        ZIP_CODE = _zip_code
        _distance_from = int(ENTRY_COMPONENTS['tk_entry_distance_from'].get())
        HAS_AREA_CHANGED = HAS_AREA_CHANGED or (_distance_from != DISTANCE_FROM)
        DISTANCE_FROM = _distance_from
        [FRAMES[each].destroy() for each in FRAMES]
        if len(MENUS) > 0:
            kwargs['menu'].delete(0, len(MENUS))
    # start for the 1st time
    else:
        IS_CLOSING = False
        tk_window.title('-- Shch Air Quality --')
        try:
            tk_window.iconbitmap(_ico_file_path)
        except:
            pass

    tk_menu = tk.Menu(tk_window)
    tk_window.config(menu= tk_menu)
    MENUS = dict()

    MENUS['tk_menu_api_key'] =  tk.Menu(tk_menu, font=('TkTextFont', fnc_font(tercero=1)))
    tk_menu.add_cascade(label= 'API Key', menu= MENUS['tk_menu_api_key'])
    MENUS['tk_menu_api_key'].add_command(\
            label= 'Change API key',\
            command= lambda: fnc_requestToChangeApiKey(tk_window, API_KEY, ico_path=_ico_file_path))

    MENUS['tk_menu_display'] =  tk.Menu(tk_menu, font=('TkTextFont', fnc_font(tercero=1)))
    tk_menu.add_cascade(label= 'Display', menu= MENUS['tk_menu_display'])
    MENUS['tk_menu_display'].add_command(label= '|+| Larger Buttons', command= lambda: fnc_regDisplay(tk_window, 1, menu = tk_menu))
    MENUS['tk_menu_display'].add_command(label= '|-| Smaller Buttons', command= lambda: fnc_regDisplay(tk_window, -1, menu = tk_menu))

    FRAMES =  dict() # holds frames
    RENEWABLE_COMPONENTS = dict() # holds tk widgets to renew after each request
    ENTRY_COMPONENTS = dict()  # holds entry widgets that specify zip_code and distance_from
    # frame for request data
    FRAMES['tk_frame_request_data'] = tk.Frame(tk_window)
    FRAMES['tk_frame_request_data'].pack(padx= 4, pady= 4)
    # frame for aqis
    FRAMES['tk_frame_air_data'] = tk.Frame(tk_window)
    FRAMES['tk_frame_air_data'].pack(padx= 4, pady= 4)

    tk_label_zip_code = tk.Label(
                FRAMES['tk_frame_request_data'],
                text = "Zip Code (5 digits)", font = ('Times', fnc_font(segundo=1)),
                padx = 12, pady = 10,
                relief = tk.SUNKEN, bd = 8
                )
    tk_label_distance_from = tk.Label(
                FRAMES['tk_frame_request_data'],
                text = "Distance From (miles)", font = ('Times', fnc_font(segundo=1)),
                padx = 2, pady = 10,
                relief = tk.SUNKEN, bd = 8
                )
    tk_label_okay = tk.Label(
                FRAMES['tk_frame_request_data'],
                text = "Renew Data", font = ('Times', fnc_font(segundo=1)),
                padx = 12, pady = 10,
                relief = tk.SUNKEN, bd = 8
                )

    ENTRY_COMPONENTS['tk_entry_zip_code'] = tk.Entry(
                FRAMES['tk_frame_request_data'],
                font= ('TkTextFont', fnc_font(primero=1)), justify='center',
                relief = tk.GROOVE, bd = 7,
                )
    ENTRY_COMPONENTS['tk_entry_zip_code'].insert('end', ZIP_CODE)
    ENTRY_COMPONENTS['tk_entry_distance_from'] = tk.Entry(
                FRAMES['tk_frame_request_data'],
                font= ('TkTextFont', fnc_font(primero=1)), justify='center',
                relief = tk.GROOVE, bd = 7,
                )
    ENTRY_COMPONENTS['tk_entry_distance_from'].insert('end', DISTANCE_FROM)
    tk_button_okay = tk.Button(
                FRAMES['tk_frame_request_data'],
                text='OKAY', font = ('Arial', fnc_font(segundo=1)), fg = 'green',
                relief = tk.GROOVE, bd = 7,
                command= lambda: fnc_renew(tk_window),
                )

    tk_label_zip_code.grid(row=0, column=0, sticky='nesw',)
    tk_label_distance_from.grid(row=0, column=1, sticky='nesw',)
    tk_label_okay.grid(row=0, column=2, sticky='nesw',)
    ENTRY_COMPONENTS['tk_entry_zip_code'].grid(row=1, column=0, pady=20,)
    ENTRY_COMPONENTS['tk_entry_distance_from'].grid(row=1, column=1, pady=20,)
    tk_button_okay.grid(row=1, column=2,)

    if (API_KEY is None) or (API_KEY == ''):
        fnc_requestToChangeApiKey(tk_window, '', ico_path=_ico_file_path, loading=1)

    return (API_KEY, ENTRY_COMPONENTS['tk_entry_zip_code'].get(), ENTRY_COMPONENTS['tk_entry_distance_from'].get())
#!
# paints the buttom frame. It is to be invoked each time after teh air data have been renewed.
# Args:
#   tk_window : tkinter window created via the tk.Tk(...) method.
# Returns : nothing.
def fnc_paint(tk_window, air_data):
    global IS_CLOSING, FRAMES, RENEWABLE_COMPONENTS

    if IS_CLOSING:
        return

    if len(RENEWABLE_COMPONENTS) > 0:
        [RENEWABLE_COMPONENTS[_wg_key].destroy() for _wg_key in RENEWABLE_COMPONENTS]

    _air_data_okay = True
    if (not isinstance(air_data, dict)) or (not ('data_full' in air_data)) or (not ('data_time' in air_data)):
        _air_data_okay = False
    elif (not isinstance(air_data['data_full'], dict)) or (not(type(air_data['data_time']) == type(''))):
        _air_data_okay = False

    _wrap_length = int((1./3.5)*tk_window.winfo_screenwidth())

    if not _air_data_okay:
        RENEWABLE_COMPONENTS['tk_label_air_data_info'] = tk.Label(
                    FRAMES['tk_frame_air_data'],
                    text = '--- AQI Values ---', font = ('Times', fnc_font(segundo=1)),
                    wraplength = _wrap_length,
                    padx = 12, pady = 4,
                    relief = tk.RAISED, bd = 3
                    )
        RENEWABLE_COMPONENTS['tk_label_air_data_warning'] = tk.Label(
                    FRAMES['tk_frame_air_data'],
                    text = '-- Cannot be Found for the Selected Area --', font = ('Times', fnc_font(segundo=1)),
                    wraplength = _wrap_length,
                    padx = 12, pady = 4,
                    relief = tk.RAISED, bd = 3
                    )

        RENEWABLE_COMPONENTS['tk_label_air_data_info'].grid(row=0, column=0, sticky='nesw')
        RENEWABLE_COMPONENTS['tk_label_air_data_warning'].grid(row=1, column=0, sticky='nesw')
        return

    RENEWABLE_COMPONENTS['tk_label_air_data_time'] = tk.Label(
                FRAMES['tk_frame_air_data'],
                text = air_data['data_time'], font = ('Times', fnc_font(tercero=1)),
                wraplength = _wrap_length,
                padx = 12, pady = 4,
                relief = tk.FLAT, bd = 3
                )
    RENEWABLE_COMPONENTS['tk_label_air_data_info'] = tk.Label(
                FRAMES['tk_frame_air_data'],
                text = '--- AQI Values ---', font = ('Times', fnc_font(segundo=1)),
                wraplength = _wrap_length,
                padx = 12, pady = 4,
                relief = tk.RAISED, bd = 3
                )

    _namePairs = list()
    for _element in air_data['data_full']:
        _nameRoot = 'tk_label_air_data_' + _element + '_'
        _name_pair = (_nameRoot + 'aqi', _nameRoot + 'quality')
        _namePairs.append(_name_pair)
        _aqi, _quality, _q_index, _fg, _bg = air_data['data_full'][_element]
        _aqi = int(float(_aqi)*100.)/100
        _aqi_text = '{}: {}'.format(_element, _aqi)
        _quality_text = '{} (Quality Index: {})'.format(_quality, _q_index)

        RENEWABLE_COMPONENTS[_name_pair[0]] = tk.Label(
                    FRAMES['tk_frame_air_data'],
                    text = _aqi_text, font = ('Times', fnc_font(segundo=1)),
                    wraplength = _wrap_length,
                    padx = 12, pady = 4,
                    relief = tk.SUNKEN, bd = 3
                    )
        RENEWABLE_COMPONENTS[_name_pair[1]] = tk.Label(
                    FRAMES['tk_frame_air_data'],
                    text = _quality_text, font = ('Times', fnc_font(segundo=1)),
                    fg = _fg, bg = _bg,
                    wraplength = _wrap_length,
                    padx = 12, pady = 4,
                    relief = tk.SUNKEN, bd = 3
                    )

    RENEWABLE_COMPONENTS['tk_label_air_data_time'].grid(row=0, column=0, sticky='nesw')
    RENEWABLE_COMPONENTS['tk_label_air_data_info'].grid(row=1, column=0, columnspan=2, sticky='nesw')
    _row = 2
    for _name_pair in _namePairs:
        RENEWABLE_COMPONENTS[_name_pair[0]].grid(row=_row, column=0, sticky='nesw')
        RENEWABLE_COMPONENTS[_name_pair[1]].grid(row=_row, column=1, sticky='nesw')
        _row +=1
    # end of function
#!
# destroys tk_window. Before that it sets IS_CLOSING to True to prevent any attempts to paint.
# Args:
#   tk_window : tkinter window created via the tk.Tk(...) method.
# Returns : nothing.
def fnc_paintStop(tk_window):
    global IS_CLOSING
    IS_CLOSING = True
    fnc_save()
    tk_window.destroy()
    # end of function

#!
# changes the API key.The new API key is stored in API_KEY (global variable).
def fnc_changeApiKey(api_key):
    global API_KEY

    API_KEY = api_key
    # end of function
#!
# starts a request to changes the API key.
def fnc_requestToChangeApiKey(tk_window, api_key, **kwargs):
    _akc = AKC(tk_window, api_key, fnc_changeApiKey, **kwargs)
    _akc.top.focus_set()
    _akc.top.grab_set()
    _akc.top.wait_window()

    if not ('loading' in kwargs) and not (_akc.IS_CANCELED):
        if DEBUG:
            print('changing...')
        fnc_renew(tk_window)
    # end of function

#!
# checks varaible type
# Args:
#   type_of_var: str
#       Describes the type. It can be be presently str, int and dict.
# Returns: success_code : bool
#   This is True is the check has passed. False otherwise.
def fnc_checkType(type_of_var, var_to_check):
    if type_of_var == 'str':
        return type('') == type(var_to_check)

    if type_of_var == 'int':
        return type(0) == type(var_to_check)

    if type_of_var == 'dict':
        return isinstance(var_to_check, dict)

    return False
#!
#
def fnc_load():
    global DEBUG
    global HOME_DIR, CONFIG_FOLDER, ICO_FILE, CURRENT_USER
    global API_KEY, ZIP_CODE, DISTANCE_FROM, WIDGET_FONT_SIZE_INDEX

    HOME_DIR = os.path.dirname(os.path.abspath(__file__))
    CURRENT_USER = getpass.getuser()
    _config_folder_path = os.path.join(HOME_DIR, CONFIG_FOLDER)
    _config_file_path = os.path.join(_config_folder_path, '{}.cfg'.format(CURRENT_USER))
    if DEBUG:
        print(_config_file_path)

    _CONFIG_KEYS = {\
        'ICO_FILE' : 'str',\
        'API_KEY' : 'str', 'ZIP_CODE' : 'str', 'DISTANCE_FROM' : 'int',\
        'WIDGET_FONT_SIZE_INDEX' : 'int'}
    _useDefaults = True
    # try to load from the config file. If not available, use the default settings
    try:
        with open(_config_file_path, 'r') as _config_file:
            _config = json.load(_config_file)
            __c__ = {_key : _config[_key] for _key in _CONFIG_KEYS if\
                    fnc_checkType(_CONFIG_KEYS[_key], _config[_key])}
            if DEBUG:
                print(__c__)

            if len(__c__) == len(_CONFIG_KEYS):
                _useDefaults = False
    except:
        if DEBUG:
            print('no config is loaded')

    if _useDefaults:
        ICO_FILE = 'shch_071821_121644.ico'
        API_KEY = ''
        ZIP_CODE = '20500'
        DISTANCE_FROM = 30
        WIDGET_FONT_SIZE_INDEX = 7
    else:
        ICO_FILE = __c__['ICO_FILE']
        API_KEY = __c__['API_KEY']
        ZIP_CODE = __c__['ZIP_CODE']
        DISTANCE_FROM = __c__['DISTANCE_FROM']
        WIDGET_FONT_SIZE_INDEX = __c__['WIDGET_FONT_SIZE_INDEX']
        # end of fnc_load
#!
# saves the existing configuration in the file named 'current user name'.cfg, which is located in
#   the folder named shch_img_browser_cfg.
# Args: none.
# Returns: nothing.
def fnc_save():
    global DEBUG
    global HOME_DIR, CONFIG_FOLDER, ICO_FILE, CURRENT_USER
    global API_KEY, ENTRY_COMPONENTS, WIDGET_FONT_SIZE_INDEX

    _config_folder_path = os.path.join(HOME_DIR, CONFIG_FOLDER)
    if not os.path.isdir(_config_folder_path):
        try:
            os.mkdir(_config_folder_path)
        except:
            return

    _config_file_path = os.path.join(_config_folder_path, '{}.cfg'.format(CURRENT_USER))

    try:
        with open(_config_file_path, 'w') as _config_file:
            __c__ = dict()

            __c__['ICO_FILE'] = ICO_FILE
            if DEBUG:
                print(__c__['ICO_FILE'])

            __c__['API_KEY'] = API_KEY
            if DEBUG:
                print(__c__['API_KEY'])

            __c__['ZIP_CODE'] = ENTRY_COMPONENTS['tk_entry_zip_code'].get()
            if DEBUG:
                print(__c__['ZIP_CODE'])

            __c__['DISTANCE_FROM'] = int(ENTRY_COMPONENTS['tk_entry_distance_from'].get())
            if DEBUG:
                print(__c__['DISTANCE_FROM'])

            __c__['WIDGET_FONT_SIZE_INDEX'] = WIDGET_FONT_SIZE_INDEX
            if DEBUG:
                print(__c__['WIDGET_FONT_SIZE_INDEX'])

            _config_to_save = json.dumps(__c__)
            _config_file.write(_config_to_save)

    except:
        if DEBUG:
            print('no config is saved')

#!
# renews Air data.
# Args:
#   zip_code : str
#       The zip code of the area for which to get air quality data
#   distance_from: int or str or float
#       This must be convertable to int, and is measured in miles.
# Returns : dict
#   The structure is {'data_full' :  dict, 'data_time' : str}
#       The 1st member ('data_full') is a dictionary with the structure as shown in the example below.
#       Example : {
#               'OZONE': (16.571428571428573, 'Good', 1, '#000', '#00E400'),
#               'PM2.5': (8.5, 'Good', 1, '#000', '#00E400'),
#               'PM10': (8.0, 'Good', 1, '#000', '#00E400'),
#               'NO2': (1.0, 'Good', 1, '#000', '#00E400'),
#               'SO2': (0.0, 'Good', 1, '#000', '#00E400'),
#               'CO': (-999.0, 'Good', 1, '#000', '#00E400')
#               }
#       The 2nd member ('data_time') is a string in the format year-month-day : hour.
#       2019-09-30 : 10
def fnc_renewAirData(api_key, zip_code, distance_from):
    global DEBUG, GET_AIR_DATA, AIR_DATA_TIMEOUT

    if DEBUG:
        air_quality = AQI.AirQuality(api_key, zip_code, int(distance_from), ON_SCREEN=1)
        if GET_AIR_DATA:
            air_quality.getAirData(timeout=AIR_DATA_TIMEOUT)
            air_quality.printAirData()
        else:
            air_quality.data_full = {
                      'OZONE': (16.571428571428573, 'Good', 1, '#000', '#00E400'),
                      'PM2.5': (8.5, 'Good', 1, '#000', '#00E400'),
                      'PM10': (8.0, 'Good', 1, '#000', '#00E400'),
                      'NO2': (1.0, 'Good', 1, '#000', '#00E400'),
                      'SO2': (0.0, 'Good', 1, '#000', '#00E400'),
                      'CO': (-999.0, 'Good', 1, '#000', '#00E400')
                      }
            air_quality.data_time = '2019-09-30 : 10'
    # normal operation
    else:
        air_quality = AQI.AirQuality(api_key, zip_code, int(distance_from))
        if GET_AIR_DATA:
            air_quality.getAirData(timeout=AIR_DATA_TIMEOUT)

    return {'data_full' : air_quality.data_full, 'data_time' : air_quality.data_time}
    # end of function
#!
# callback for the OKAY button. It renews the air data (via a call to fnc_renewAirData(...)),
#   and updates the 2nd frame (via a call to fnc_paint(...))
def fnc_renew(tk_window):
    global API_KEY, ENTRY_COMPONENTS#, RENEWABLE_COMPONENTS
    global AIR_DATA

    # try:
    #     RENEWABLE_COMPONENTS['tk_label_air_data_info'].config(text='Fetching Data')
    # except:
    #     pass

    AIR_DATA = fnc_renewAirData(\
        API_KEY,\
        ENTRY_COMPONENTS['tk_entry_zip_code'].get(),\
        ENTRY_COMPONENTS['tk_entry_distance_from'].get())
    fnc_paint(tk_window, AIR_DATA)
    # end of function

if __name__ == "__main__":

    tk_window_main = tk.Tk()
    tk_window_main.protocol("WM_DELETE_WINDOW", lambda: fnc_paintStop(tk_window_main))
    # centering the window...
    screen_width = int((1./2.)*tk_window_main.winfo_screenwidth())
    screen_x = int((tk_window_main.winfo_screenwidth() - screen_width)/2.)
    screen_height = int((1./1.9)*tk_window_main.winfo_screenheight())
    tk_window_main.geometry('{}x{}+{}+{}'.format(screen_width, screen_height, screen_x, 0))
    fnc_load()
    api_key, zip_code, distance_from = fnc_paintStart(tk_window_main)
    # tk_window_main.mainloop()
    AIR_DATA = fnc_renewAirData(api_key, zip_code, distance_from)
    fnc_paint(tk_window_main, AIR_DATA)

    tk_window_main.mainloop()

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
