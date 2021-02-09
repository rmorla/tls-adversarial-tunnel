#!/bin/bash
mkdir /root/environments/tls/certs/certs-client
mkdir /root/environments/tls/certs/certs-server

echo "[ req ]
default_bits = 2048
default_md = sha256
prompt = no
encrypt_key = no
distinguished_name = dn
req_extensions = req_ext
[ dn ]
C = CH
O = org
CN = client1
[ req_ext ]
subjectAltName = DNS:client1" >> client1.cfg

openssl req -new -config client1.cfg -newkey rsa:2048 -days 365 -nodes -x509 -keyout client.key -out client.crt
cp client.crt /root/environments/tls/certs/certs-server
mv client.key client.crt client1.cfg /root/environments/tls/certs/certs-client

echo "[ req ]
default_bits = 2048
default_md = sha256
prompt = no
encrypt_key = no
distinguished_name = dn
req_extensions = req_ext
[ dn ]
C = CH
O = org
CN = tunnel-server
[ req_ext ]
subjectAltName = DNS:tunnel-server" >> server1.cfg

openssl req -new -config server1.cfg -newkey rsa:2048 -days 365 -nodes -x509 -keyout server.key -out server.crt
cp server.crt /root/environments/tls/certs/certs-client
mv server.key server.crt server1.cfg /root/environments/tls/certs/certs-server
c_rehash /root/environments/tls/certs/certs-server
