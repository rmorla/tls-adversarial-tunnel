# TLS Adversarial Proxy Tunnel

A Python TLS tunnel to send IP packets over a secure connection.

## Usage

There are two machines, a client and server, which communicate in a public network (``10.0.0.0/24``).  
The server also has access to a private network (``10.1.1.0/24``) giving access to the client through the TLS tunnel.

### Server install
Python should be already pre-installed.  
Install pip and other tools:
```bash
sudo apt install -y python3-pip
sudo apt install -y build-essential python3-dev
```
Setup and activate a Virtual Environment:
```bash
sudo apt install -y python3-venv
mkdir ~/environments && cd ~/environments
python3 -m venv tls --copies

source ~/environments/tls/bin/activate
```
Give ``CAP_NET_ADMIN`` capability to the Python executable, so that it can create/manage TUN/TAP interfaces:

```bash
sudo setcap cap_net_admin=+pe ~/environments/tls/bin/python
```

Install pytun and token-bucket:
```bash
pip install git+https://github.com/montag451/pytun
pip install token-bucket
```

Create a *self-signed* server certificate:
```
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout server.key -out server.crt
```
Details don't matter, just make sure to use ``tunnel-server`` as Common Name, or change the code accordingly.  
Give ``server.crt`` (the *self-signed certificate*) to the client.  
**Keep ``server.key`` private!** (the *private key*)

### Client install
The code is meant to run on a Windows machine.

Install Python 3 (https://www.python.org/downloads/), and then install the required dependencies:
```
pip install pywin32 scapy 
```

Also install a TAP interface for Windows, such as the ones made by OpenVPN (http://build.openvpn.net/downloads/releases/)

Afterwards, create a client certificate:
```
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout client.key -out client.crt
```
Common Name doesn't matter here.  
Once again, give ``client.crt`` to the server, and **keep ``client.key`` private**.

### Running
Place the client certificates in a folder named ``certs/`` and then use ``c_rehash`` to calculate the hashes of the certificates and to create the necessary symlinks.

Then, run ``server.py`` and create a bridge between the tap interface and the interface connected to the private network.
Next, after running ``client.py`` on the client machine, packets should start flowing.
