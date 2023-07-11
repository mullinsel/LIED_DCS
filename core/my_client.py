# my_client.py

from msl.loadlib import Client64
import threading
import sys
sys.path.insert(0,'C:\\Users\cbonline\Documents\CC_TDC-main\interface\pyxxusb\\')

class MyClient(Client64):
    """Call a function in 'my_lib.dll' via the 'MyServer' wrapper."""

    def __init__(self):
        # Specify the name of the Python module to execute on the 32-bit server (i.e., 'my_server')
        super(MyClient, self).__init__(module32='my_server')

    def __getattr__(self,name):
        def send(*args, **kwargs):
            return self.request32(name,*args, **kwargs)
        return send
