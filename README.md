# TLS Adversarial Proxy Tunnel

A Python TLS tunnel to send IP packets over a secure connection.

## Docker, usage

Build images

- cd mininet; docker build --tag mininet .
- cd tls-tunnel; docker build --tag tls-tunnel .

Setup
- Edit .env file with your settings

Generate keys
- docker-compose -f stack-genkeys.yml -p tunnel up

Run
- docker-compose -f stack.yml -p tunnel up


## Windows client

- see windows folder
