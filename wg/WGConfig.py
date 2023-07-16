from wg import WGKey


class WGConfig:

    def __init__(self, private_key, local_ip, listen_port):
        self.postup = None
        self.postdown = None
        self.peers = []
        self.private_key = private_key
        self.local_ip = local_ip
        self.listen_port = listen_port
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
