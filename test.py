from wireguard_tools import *
from python_wireguard import *


device = WireguardDevice.get("wg0")
wgconfig = device.get_config()
print(wgconfig.asdict())
