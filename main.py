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
    print("PRIVATE", private.as_str())
    print("PUBLIC", public_key.as_str())
    config = WGConfig(private, "10.200.200.1/24", 51820)
    config.set_postup(
        "iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A "
        "POSTROUTING -o eth0 -j MASQUERADE"
    )
    config.set_postdown(
        "iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D "
        "POSTROUTING -o eth0 -j MASQUERADE"
    )
    serv = WGDevice("wg0", config)
    serv.enable()
    # wgconfig.addresses.insert(0, "10.200.200.1/24")
    session.post("/register", json={"public_key": public_key.as_str()})
    return private, public_key, serv


def add(server, public_c, i):
    print("recieved", public_c)
    client_key = WGKey(bytes(public_c, "utf-8"))
    print("saved", client_key.as_str())
    client_ip = f"10.200.200.{i}/32"
    _, preshared = WGKey.generate_key_pair()
    client = WGPeer(client_ip, client_key, preshared)
    server.add_peer(client)
    return preshared.as_str()


private_key, public_key, server = boot()


@app.route("/check", methods=["GET"])
def check():
    return "1"


@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.json
    return {
        "0public_key": public_key.as_str(),
        "1presharedkey": add(server, data["public_key"], data["i"]),
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
