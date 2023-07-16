import subprocess

from flask import Flask, request
import os
from requests_toolbelt import sessions
from dotenv import load_dotenv

from wg import WGConfig, WGPeer, WGKey, WGDevice

app = Flask(__name__)
load_dotenv()
session = sessions.BaseUrlSession(base_url=os.getenv("CONTROLLER_URL"))


def boot():
    name = "wg2"
    listen_port = 51822
    local_ip = "10.200.200.1/24"

    WGDevice.delete_device(name)
    private, public = WGKey.generate_key_pair()
    config = WGConfig(private, local_ip, listen_port)

    dev = WGDevice(name, config)
    dev.enable()

    config.postup = ["iptables -A FORWARD -i %i -j ACCEPT", "iptables -A FORWARD -o %i -j ACCEPT",
                     "iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE"]
    config.postdown = ["iptables -D FORWARD -i %i -j ACCEPT", "iptables -D FORWARD -o %i -j ACCEPT ",
                       "iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE"]
    config.dns_servers = ['1.1.1.1', '8.8.8.8']

    filename = f'{name}.conf'
    with open(filename, 'w+') as f:
        f.write(str(config))

    file_loc = os.path.abspath(filename)
    cmd = ["wg-quick", "up", file_loc]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True
    )
    print(' '.join(cmd))
    out, err = proc.communicate()
    print("OUT", out.decode("utf-8"))
    if err:
        print("ERR", err.decode("utf-8"))

    return private, public, dev
    # WGDevice.delete_device("wg0")
    # private, public_key = WGKey.generate_key_pair()
    # print("PRIVATE", private.as_str())
    # print("PUBLIC", public_key.as_str())
    # config = WGConfig(private, "10.200.200.1/24", 51820)
    # config.set_postup(
    #     "iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A "
    #     "POSTROUTING -o eth0 -j MASQUERADE"
    # )
    # config.set_postdown(
    #     "iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D "
    #     "POSTROUTING -o eth0 -j MASQUERADE"
    # )
    # serv = WGDevice("wg0", config)
    # serv.enable()
    # # wgconfig.addresses.insert(0, "10.200.200.1/24")
    # session.post("/register", json={"public_key": public_key.as_str()})



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
