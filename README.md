# TLS Adversarial Proxy Tunnel

A Python TLS tunnel to send IP packets over a secure connection.

## Usage

- cd mininet; doker build -tag mininet .
- cd tls-tunnel; doker build -tag tls-tunnel .
- Edit .env file with your settings
- docker-compose -f stack.yml -p tunnel 
