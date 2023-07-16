import os
import re
import subprocess
from ctypes import CDLL, c_ushort, create_string_buffer

from wireguard_tools import WireguardDevice, WireguardKey

from wg import WGConfig, WGPeer
from wg.CInterface import c_library


class WGDevice:
    def __init__(self, name, config: WGConfig):
        if not self.__is_valid_interface(name):
            raise ValueError(f"Invalid interface name {name}")
        self.name = name
        self.config = config
        self.interface_created = False
        self.peers = []

    @staticmethod
    def __is_valid_interface(interface):
        return bool(re.match("^[A-Za-z0-9_-]*$", interface))

    def enable(self):
        if not self.interface_created:
            self.create_interface()
        os.system(f"ip link set up {self.name}")

    def add_peer(self, peer: WGPeer):
        self.peers.append(peer)
        print("Client key", peer.client_key.as_bytes())
        # print(peer.client_key.as_bytes())
        c_library.add_client_peer(
            self.name.encode(), peer.client_key.as_bytes(), peer.client_ip.encode()
        )
        c_library.list_devices()
        # device = WireguardDevice.get("wg0")
        # wgconfig = device.get_config()
        # pr = peer.preshared.as_str()
        # print("PR", wgconfig.peers)
        # wgconfig.peers[WireguardKey(peer.client_key.as_str())].preshared_key = pr
        # wgconfig.peers[WireguardKey(peer.client_key.as_str())].allowed_ips = [
        #     peer.client_ip
        # ]
        # device.set_config(wgconfig)

    @staticmethod
    def delete_device(name):
        c_library.delete_device(name.encode())

    @staticmethod
    def get_device(name):
        pass

    def get_conf(self):
        proc = subprocess.Popen(
            ["wg", "showconf", self.name], stdout=subprocess.PIPE, shell=True
        )
        out, _ = proc.communicate()
        return out.decode("utf-8")

    def set_conf(self, values):
        conf = self.get_conf()
        for k, v in values.items():
            proc = subprocess.Popen(
                ["wg", "addconf", self.name, f"{k} = {v}"],
                stdout=subprocess.PIPE,
                shell=True,
            )
            out, _ = proc.communicate()
            print("conf", out)

        # print("res", out.decode("utf-8"))

    def create_interface(self):
        c_library.add_server_device(
            self.name.encode(),
            c_ushort(self.config.listen_port),
            self.config.private_key.as_bytes(),
        )
        os.system(f"ip a add dev {self.name} {self.config.local_ip}")
        additional_conf = {"PostUp": self.config.postup, "Adresses": "10.200.200.1/24"}
        self.set_conf(additional_conf)

        # os.system(f"wg set {self.name} postup {self.config.postup}")
        # os.system(f"wg set {self.name} listen-port 7200")
        os.system(self.config.postup)
        self.interface_created = True

    def __del__(self):
        os.system(self.config.postdown)
