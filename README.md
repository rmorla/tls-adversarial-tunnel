# TLS Adversarial Proxy Tunnel

A Python TLS tunnel to send IP packets over a secure connection.

## Docker, usage

- cd mininet; docker build --tag mininet .
- cd tls-tunnel; docker build --tag tls-tunnel .
- Edit .env file with your settings
- docker-compose -f stack.yml -p tunnel up


## Windows client

- see windows folder
