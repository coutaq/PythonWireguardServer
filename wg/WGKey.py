import base64
import secrets
from wg.X25519 import X25519PrivateKey


class WGKey:
    def __init__(self, key_bytes):
        self.key_bytes = key_bytes

    def get(self):
        return self.key_bytes.decode("utf-8")
    
    def as_bytes(self):
        return self.key_bytes

    @staticmethod
    def generate_key_pair():
        private = X25519PrivateKey.from_private_bytes(secrets.token_bytes(32))
        public = private.public_key()
        private_b64 = base64.b64encode(private.private_bytes())
        public_b64 = base64.b64encode(public)
        return WGKey(private_b64), WGKey(public_b64)
