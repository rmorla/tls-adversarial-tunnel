import os
import socket
import ssl
import threading
from scapy.all import *
from scapy.layers.l2 import Ether

def pkt_test(pkt, mac):
    return pkt[Ether].src == mac

def pkt_send(pkt, conn, pkts_rcvd):
    conn.send(bytes(pkt))
    pkts_rcvd[0] = pkts_rcvd[0]+1

def ThreadTapFunction(tap_interface,conn,mac_add,pkts_rcvd):
    print("Tap Thread Started")
    sniff(iface=tap_interface, lfilter = lambda y: pkt_test(y, mac_add), prn = lambda x:pkt_send(x,conn,pkts_rcvd))

server_addr = '10.0.0.1'
server_port = 8082
server_sni_hostname = 'tunnel-server'

server_cert = 'server.crt'
client_cert = 'client.crt'
client_key  = 'client.key'

tap_interface = 'tap0'
tap_mac_address = Ether().src

pkts_rcvd = [0]
pkts_sent = 0

# change console size and title
os.system('mode 60,6')
os.system('title TLS Tunnel Client')
print("Source MAC address: {}".format(Ether().src))

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
conn.connect((server_addr, server_port))

print("SSL Connection Established.")
t = threading.Thread(target=ThreadTapFunction, args=(tap_interface,conn,tap_mac_address,pkts_rcvd,))
t.daemon = True
t.start()

while True:
    print("\rPackets sent:\t{:7d} | Packets received:\t{:7d}".format(pkts_sent, pkts_rcvd[0]), end='')
    try:
        data = conn.recv(1504)
        if data:
            sendp(bytes(data), iface=tap_interface, verbose=False)
            pkts_sent+=1
    except:
        print("Exception occurred")
        raise
        break
