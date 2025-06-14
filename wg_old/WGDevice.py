import os
import re
from ctypes import CDLL, c_ushort, create_string_buffer

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

    def add_peer(self, peer:WGPeer):
        self.peers.append(peer)
        print(peer.client_key.as_bytes())
        c_library.add_client_peer(self.name.encode(), peer.client_key.as_bytes(), peer.client_ip.encode())
        
    @staticmethod
    def delete_device(name):
        c_library.delete_device(name.encode())

    @staticmethod
    def get_device(name):
        pass

    def create_interface(self):
        c_library.add_server_device(self.name.encode(),  c_ushort(self.config.listen_port), self.config.private_key.as_bytes())
        os.system(f"ip a add dev {self.name} {self.config.local_ip}")
        os.system(self.config.postup)
        self.interface_created = True

    def __del__(self):
        os.system(self.config.postdown)
