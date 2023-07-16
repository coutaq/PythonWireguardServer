from flask import Flask, request
import os
from requests_toolbelt import sessions
from dotenv import load_dotenv

from wg import WGConfig, WGPeer, WGKey, WGDevice

app = Flask(__name__)
load_dotenv()
session = sessions.BaseUrlSession(base_url=os.getenv("CONTROLLER_URL"))

def boot():
    WGDevice.delete_device("wg0")
    private, public_key = WGKey.generate_key_pair()
    config = WGConfig(private, "10.200.200.1/24", 51820)
    config.set_postup("iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A "
                      "POSTROUTING -o eth0 -j MASQUERADE")
    config.set_postdown("iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D "
                        "POSTROUTING -o eth0 -j MASQUERADE")
    serv = WGDevice("wg0", config)
    serv.enable()
    # wgconfig.addresses.insert(0, "10.200.200.1/24")
    session.post("/register", json={"public_key": public_key.__str__()})
    return private, serv
def add(server, public_c, i):
    print(public_c)
    client_key = WGKey(public_c)
    client_ip = f"10.200.200.{i}/32"

    _, preshared = WGKey.generate_key_pair()
    client = WGPeer(client_ip, client_key)
    server.add_peer(client)

    # conn = ClientConnection(client_key, client_ip)
    # server.add_client(conn)
    # device = WireguardDevice.get("wg0")
    # wgconfig = device.get_config()
    # _, preshared = private_s.key_pair()
    # preshared = str(preshared)
    # wgconfig.peers[WireguardKey(public_c)].preshared_key = preshared
    # wgconfig.peers[WireguardKey(public_c)].allowed_ips = [client_ip]
    # device.set_config(wgconfig)
    # print(wgconfig)
    return preshared


private_key, server = boot()


@app.route("/check", methods=["GET"])
def check():
    return "1"

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.json
    return {"presharedkey": add(server, data["public_key"], data["i"])}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
