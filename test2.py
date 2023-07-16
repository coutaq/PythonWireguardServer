import os
import subprocess

from wg import WGKey, WGConfig, WGDevice

name = "wg2"
listen_port = 51822
local_ip = "10.200.200.1/24"

WGDevice.delete_device(name)
private, public = WGKey.generate_key_pair()
config = WGConfig(private, local_ip, listen_port)

dev = WGDevice(name, config)
dev.enable()

config.postup = ["iptables -A FORWARD -i %i -j ACCEPT", "iptables -A FORWARD -o %i -j ACCEPT", "iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE"]
config.postdown = ["iptables -D FORWARD -i %i -j ACCEPT","iptables -D FORWARD -o %i -j ACCEPT ","iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE"]
config.dns_servers = ['1.1.1.1', '8.8.8.8']


filename = f'{name}.conf'
with open(filename, 'w+') as f:
    f.write(str(config))

file_loc = os.path.abspath(filename)
cmd =  ["wg-quick", "up", file_loc]
proc = subprocess.Popen(
   cmd, stdout=subprocess.PIPE, shell=True
)
print(' '.join(cmd))
out, err = proc.communicate()
print("OUT", out.decode("utf-8"))
if err:
    print("ERR", err.decode("utf-8"))