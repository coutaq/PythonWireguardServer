from wg import WGKey


class WGPeer:
    def __init__(self, client_ip, client_key, preshared):
        self.client_ip = client_ip
        self.client_key = client_key
        self.preshared = preshared
