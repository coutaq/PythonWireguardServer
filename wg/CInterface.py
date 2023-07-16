import os
from ctypes import CDLL

dirname = os.path.dirname(os.path.realpath(__file__))
c_library = CDLL(dirname + '/bin/py-wireguard.so')
