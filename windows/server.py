#!/usr/bin/env python
import socket
from socket import AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, SHUT_RDWR
import ssl

import threading

from pytun import TunTapDevice, IFF_TAP, IFF_NO_PI

import errno
import fcntl, os
import select

from time import sleep

import token_bucket

# Main thread receives user input, a server thread waits for new
# connections and serves them, TAP thread reads the interface and
# sends the packets to every open connection.

# The server thread calls a new thread for each client to deal with
# the TCP connection, reading received packets and putting them on 
# the TAP interface.

def ServerFunction(listen_addr, listen_port, conn_list, buckets):
	bindsocket = socket.socket()
	bindsocket.bind((listen_addr, listen_port))
	bindsocket.listen(5)

	print("Waiting for clients")
	# Wait for new connections and serve them, creating a thread for each client
	while True:
		newsocket, fromaddr = bindsocket.accept() # blocking call
		client_thread = threading.Thread(target=ClientThread, args=(newsocket,fromaddr,tap,conn_list,buckets,))
		client_thread.daemon = True; client_thread.start()

def ThreadTapFunction(tap,conn_list):
	# Check for packets in tap interface and send them to every active connection
	print("Tap thread started")
	while True:
		try:
			buf = tap.read(tap.mtu)
			# Insert first 2 bytes indicating actual size.
		except Exception as e:
			if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
				# Not an actual error, just no data to read yet
				# (this is expected, wait some more)
				sleep(0.1)
				# If we wish to insert a "fake packet", fill 'buf'
				# Otherwise, "continue", forcing a new tap read 
				continue
			else:
				# Actual error - raise!
				print(e)
				raise

		for conn in conn_list:
			# Do not send when client is not the destination? / Apply some filtering here.
			# Decide if we should add padding to a given packet.
			if conn['kill_signal'] == False:
				try:
					conn['socket'].send(buf)
				except OSError as exc:
					print("Error while sending data to {}:{} ({})".format(conn['ip'], conn['port'], conn['CN']))
					if exc.errno == errno.EPIPE:
						print("Broken pipe. Sending kill signal...")
						conn['kill_signal'] = True


def ClientThread(clientsocket, addr, clienttap, conn_list, buckets):
	print("New TCP Connection: {}:{}".format(addr[0], addr[1]))
	try:
		conn = context.wrap_socket(clientsocket, server_side=True)
	except Exception as e:
		print("SSL connection not established.")
		print(e)
		print("")
		return
	
	print("SSL established.")
	print("Peer: {}".format(conn.getpeercert()))
	
	new_conn = {
		'ip' : addr[0],
		'port' : addr[1],
		'socket' : conn,
		'kill_signal' : False,
		'CN' : [cn for ((n,cn),) in conn.getpeercert()['subject'] if n == 'commonName'][0]
	}

	conn_list.append(new_conn)
	conn.setblocking(0)

	# Only issue rate limit warning once, to avoid spamming terminal.
	# Perhaps implement 'verbose' option where warnings are not supressed.
	first_token_warning = True

	while new_conn['kill_signal'] == False:
		try:
			ready = select.select([conn], [], [], 0.1)
			if ready[0]:
				data = conn.recv(clienttap.mtu)
				# data = conn.recv(clienttap.mtu)
				if data:
					if buckets.consume(new_conn['CN']):
						# Remove padding or fake packets. First bytes 2 dictate real size.

						# Also, apply a firewall here! (decide if a packet coming
						# from the TLS tunnel should go to the network interface)
						clienttap.write(data)
					else:
						if first_token_warning:
							first_token_warning = False
							print("Rate limit exceeded for {}:{} (CN='{}')".format(
								new_conn['ip'], new_conn['port'], new_conn['CN'] ))
		except OSError as exc:
			if exc.errno == errno.ENOTCONN:
				print("Connection to {} closed by remote host.".format(addr[0]))
				break
	conn_list.remove(new_conn)

	try:
		conn.shutdown(socket.SHUT_RDWR)
		conn.close()
		print("Connection to {}:{} ({}) closed.".format(new_conn['ip'], new_conn['port'], new_conn['CN']))
	except:
		pass



listen_addr = '10.0.0.1'
listen_port = 8082

server_cert = 'certs/server.crt'
server_key  = 'certs/server.key'

client_certs_path = 'certs/'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(capath=client_certs_path)

# List of active connections - dicts, with IP, port, socket object,
# thread signal (to kill corresponding thread), and Common Name
# example_connection = {
#	'ip' : '10.0.0.2',
#	'port' : 2000,
#	'socket' : conn,
#	'kill_signal' : False,
#	'CN' : 'client'
# }
active_connections = []

rate_per_key = 10 # frames per second
max_capacity = 20 # token capacity - defines burst size

buckets = token_bucket.Limiter(rate_per_key, max_capacity, token_bucket.MemoryStorage())

# Initialize a TAP interface and make it non-blocking
tap = TunTapDevice(flags = IFF_TAP|IFF_NO_PI, name='tap0'); tap.up()
fcntl.fcntl(tap.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

tap_thread = threading.Thread(target=ThreadTapFunction, args=(tap, active_connections,))
tap_thread.daemon = True; tap_thread.start()

t = threading.Thread(target=ServerFunction, args=(listen_addr, listen_port, active_connections, buckets,))
t.daemon = True; t.start()

print("Starting server...")
print("Available commands: close, block, list, update, exit")
while True:
	try:
		inp = input('>> ')
		if inp == "close":
			print("\nActive connections:")
			for i, connection in enumerate(active_connections):
				print("{} - {}:{} ({})".format(i, connection['ip'], connection['port'], connection['CN']))
			
			chosen_connection = input("Which connection to close? [0-{}] >> ".format(len(active_connections)-1))
			try:
				c = active_connections[int(chosen_connection)]
			except:
				pass
			else:
				confirmation = input("Terminate connection to {}:{} ({})? (Y/n) >> ".format(c['ip'], c['port'], c['CN']))
				if confirmation != "N" and confirmation != "n":
					c['kill_signal'] = True
					print("Kill signal sent.")
		
		elif inp == "block":
			print("\nActive clients:")
			cn_list = list(set([conn['CN'] for conn in active_connections]))
			for i, client in enumerate(cn_list):
				print("{} - {}".format(i, client))
			
			chosen_connection = input("Which certificate to block? [0-{}] >> ".format(len(cn_list)-1))
			try:
				chosen_cn = cn_list[int(chosen_connection)]
			except:
				pass
			else:
				confirmation = input("Terminate every connection from client [{}]? (Y/n) >> ".format(chosen_cn))
				if confirmation != "N" and confirmation != "n":
					for conn in active_connections:
						if conn['CN'] == chosen_cn:
							conn['kill_signal'] = True
							print("Kill signal sent to {}:{}.".format(conn['ip'], conn['port']))
		
		elif inp == "list":
			print("\nActive connections:")
			for i, connection in enumerate(active_connections):
				print("{} - {}:{} ({})".format(i, connection['ip'], connection['port'], connection['CN']))
			print("\nActive clients:")
			cn_list = list(set([conn['CN'] for conn in active_connections]))
			for i, client in enumerate(cn_list):
				print("{} - {}".format(i, client))
		
		elif inp == "update":
			context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
			context.verify_mode = ssl.CERT_REQUIRED
			context.load_cert_chain(certfile=server_cert, keyfile=server_key)
			context.load_verify_locations(capath=client_certs_path)
			print("Updating client certificates...")
		
		elif inp == "exit":
			print("Terminating server. Closing connections...")
			for connection in active_connections:
				connection['kill_signal'] = True
			sleep(3)
			break

	except KeyboardInterrupt as e:
		print("\nKeyboard interrupt detected. Aborting.")
		for connection in active_connections:
			connection['kill_signal'] = True
		sleep(3)
		break
