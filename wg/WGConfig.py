from io import StringIO

from wg import WGKey


class WGConfig:

    def __init__(self, private_key, local_ip, listen_port):
        self.postup = None
        self.postdown = None
        self.peers = []
        self.private_key = private_key
        self.local_ip = local_ip
        self.listen_port = listen_port
        self.dns_servers = []
        self.on_update = lambda: None

    def set_postup(self, postup):
        self.postup = postup

    def set_postdown(self, postdown):
        self.postdown = postdown

    def add_peer(self, peer):
        self.peers.append(peer)
        self.on_update()

    def remove_peer(self, peer):
        self.peers.remove(peer)
        self.on_update()

    def __str__(self):
        stt = StringIO()
        stt.write("[Interface]\n")
        stt.write(f"ListenPort = {self.listen_port}\n")
        stt.write(f"PrivateKey = {self.private_key.as_str()}\n")
        if self.postup:
            for item in self.postup:
                stt.write(f"PostUp = {item}\n")
        if self.postdown:
            for item in self.postdown:
                stt.write(f"PostDown = {item}\n")
        stt.write(f"Address = {self.local_ip}\n")
        if self.dns_servers:
            for item in self.dns_servers:
                stt.write(f"DNS = {item}\n")
        stt.seek(0)
        return stt.read()
