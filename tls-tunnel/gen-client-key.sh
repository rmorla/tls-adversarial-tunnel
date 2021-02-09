#!/bin/bash
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout client.key -out client.crt
mv client.key client.crt /root/environments/tls/certs
