import os
import tkinter as tk

DEBUG = False#True

#!
# this is a wrapper for os.path.isfile(...)
# Args:
#   file_path : str
#       The file path to check if that file exists.
# Returns: result : bool
#   The return value is that of os.path.isfile(file_path)
def fnc_IsExistingFile(file_path):
    return os.path.isfile(file_path)

class ApiKeyChange():
    #!
    def __init__(self, root, api_key, callback=None, **kwargs):
        self.callback = callback
        self.IS_CANCELED = True

        self.top = tk.Toplevel(root)
        if ('ico_path' in kwargs) and fnc_IsExistingFile(kwargs['ico_path']):
            self.top.iconbitmap(kwargs['ico_path'])

        self.label_w_info = tk.Label(
            self.top,
            text= "Enter API key", font= (14), fg= 'black',
        )
        self.entry_for_api_key = tk.Entry(
        self.top,
        font= (14),
        width= len(api_key) if (len(api_key) > 0) else 36,
        )
        self.entry_for_api_key.insert(0, api_key)

        self.button_okay = tk.Button(
            self.top,
            text= "Okay", font=(14), fg= 'black',
            relief = tk.GROOVE, bd = 4,
            command=  self.fnc_okay,
        )
        self.button_cancel = tk.Button(
            self.top,
            text= 'Cancel', font= (14), fg= 'green',
            relief = tk.RIDGE, bd = 4,
            command= self.top.destroy,
        )

        self.label_w_info.grid(row= 0, column= 0, padx= 5, pady= (2, 5), )
        self.entry_for_api_key.grid(row= 1, column= 0, padx= 7, pady= (5, 5), )
        self.button_okay.grid(row= 2, column= 0, padx= 5, pady= (4, 4), )
        self.button_cancel.grid(row= 3, column= 0, padx= 5, pady= (4, 10), )
        # end of __init__

    #!
    # changes API key.
    # Args: none
    # Returns: nothing
    def fnc_okay(self):
        _api_key = self.entry_for_api_key.get()
        self.top.destroy()

        if not (self.callback is None):
            try:
                self.callback(_api_key)
                self.IS_CANCELED = False
                if DEBUG:
                    print(api_key)
            except:
                pass
        # end of function
    # end of class ApiKeyChange
