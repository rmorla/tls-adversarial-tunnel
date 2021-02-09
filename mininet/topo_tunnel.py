from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import DockerRunning


import argparse

parser = argparse.ArgumentParser(description='TLS tunnel network topology')
parser.add_argument('--prx_srv_container', dest='prx_srv_container', type=str, default='')
parser.add_argument('--prx_srv_priv_addr', dest='prx_srv_priv_addr', type=str, default='')
parser.add_argument('--prx_cli_container', dest='prx_cli_container', type=str, default='')
parser.add_argument('--prx_cli_priv_addr', dest='prx_cli_priv_addr', type=str, default='')

parser.add_argument('--srv_container', dest='srv_container', type=str, default='')
parser.add_argument('--srv_priv_addr', dest='srv_priv_addr', type=str, default='')
parser.add_argument('--cli_container', dest='cli_container', type=str, default='')
parser.add_argument('--cli_priv_addr', dest='cli_priv_addr', type=str, default='')

globals().update(vars(parser.parse_args()))


net = Containernet(controller=Controller)
net.addController('c0')
d1 = net.addDocker('d1', ip=prx_srv_priv_addr, cls=DockerRunning, container_name=prx_srv_container)
d2 = net.addDocker('d2', ip=prx_cli_priv_addr, cls=DockerRunning, container_name=prx_cli_container)
d3 = net.addDocker('d3', ip=srv_priv_addr, cls=DockerRunning, container_name=srv_container)
d4 = net.addDocker('d4', ip=cli_priv_addr, cls=DockerRunning, container_name=cli_container)

s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
net.addLink(d1, s1)
net.addLink(d3, s1)

net.addLink(d2, s2)
net.addLink(d4, s2)

net.start()

def if_up(d):
    if1 = d.intfNames()[0]
    d.cmd('ip link set ' + if1 + ' up')

for d in [d1, d2, d3, d4]:
    if_up(d)

CLI(net)
