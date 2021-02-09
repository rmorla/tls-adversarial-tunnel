# TLS Adversarial Proxy Tunnel

A Python TLS tunnel to send IP packets over a secure connection.

## Docker, usage

Build images

- cd mininet; docker build --tag mininet .
- cd tls-tunnel; docker build --tag tls-tunnel .

Setup
- Edit .env file with your settings

Generate keys
- docker run -it -v ${ROOT_FOLDER}/certs-client:/root/environments/tls/certs tls-tunnel /root/environments/tls/gen-client-key.sh
- docker run -it -v ${ROOT_FOLDER}/certs-server:/root/environments/tls/certs tls-tunnel /root/environments/tls/gen-server-key.sh

Setup network topology
- mkdir ${ROOT_FOLDER}/mininet; cp mininet/topo_tunnel.py ${ROOT_FOLDER}/mininet/.

Run
- docker-compose -f stack.yml -p tunnel up


## Windows client

- see windows folder
