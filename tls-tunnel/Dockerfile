FROM ubuntu:18.04

RUN apt update && apt install -y python3-pip build-essential python3-dev
RUN apt install -y python3-venv
RUN mkdir /root/environments 
RUN cd /root/environments; python3 -m venv tls --copies
RUN . /root/environments/tls/bin/activate
RUN apt install -y libcap2-bin
RUN setcap cap_net_admin=+pe /root/environments/tls/bin/python
RUN apt install -y git
RUN /root/environments/tls/bin/pip install git+https://github.com/montag451/pytun

RUN /root/environments/tls/bin/pip install scapy
RUN /root/environments/tls/bin/pip install psutil
RUN /root/environments/tls/bin/pip install ipaddress

RUN apt update && apt install -y bridge-utils iproute2 uml-utilities
RUN apt update && apt install -y tcpdump iputils-ping
RUN apt install -y vim

COPY genkeys.sh /root/environments/tls/genkeys.sh
RUN chmod a+x /root/environments/tls/genkeys.sh

COPY tunnel.py /root/environments/tls/tunnel.py
#folder for client public keys in the server 
RUN mkdir /root/environments/tls/certs
