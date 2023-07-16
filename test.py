from wg import WGConfig, WGPeer, WGKey, WGDevice

private, public_key = WGKey.generate_key_pair()
print(private, public_key)
# private, public_key = Key().key_pair()
# print(private, public_key)