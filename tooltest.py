from wireguard_tools import *
from pyroute2 import NDB, WireGuard

IFNAME = 'wg1'

# Create a WireGuard interface
with NDB() as ndb:
    with ndb.interfaces[IFNAME] as dev:
        dev.remove()
    with ndb.interfaces.create(kind='wireguard', ifname=IFNAME) as link:
        link.add_ip("10.200.200.1/24")
        link.set(state='up')

private_key = WireguardKey.generate()
public_key = private_key.public_key()
print(private_key)
wg = WireGuard()
wg.set(IFNAME, private_key=str(private_key),
       fwmark=0x1337, listen_port=51821)

device = WireguardDevice.get(IFNAME)
wgconfig = device.get_config()
wgconfig.postup = ["iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE"]
wgconfig.postdown = ["iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE"]
wgconfig.addresses = ["10.200.200.1/24"]
wgconfig.dns_servers = ['1.1.1.1','8.8.8.8']
test = wgconfig.to_resolvconf()
print(wgconfig)