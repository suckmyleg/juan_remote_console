from console.CONNECTION import CONNECTION
import socket
import threading

class SERVER:
	def accept_connections(self):
		while self.accept_new_connections:
			conn, addr = self.s.accept()
			p = CONNECTION(conn, addr, self.bridge)
			self.connections.append(p)

	def setup(self, pr=print, inp=input):
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.s.bind((self.host, self.port))
			self.s.listen()
			if not self.accept_new_connections_thread:
				self.accept_new_connections = True
				self.accept_new_connections_thread = threading.Thread(target=self.accept_connections)
				self.accept_new_connections_thread.start()
				pr("Running server on:\nPort: {}\nHost: {}".format(self.port, self.host))
			else:
				pr("Already accepting new connections")
		except Exception as e:
			pr("Error trying to setup the server.\nHost: {}\nPort: {}\nError: {}".format(self.host, self.port, e))

	def __init__(self, host, port, bridge):
		self.host = host
		self.port = port
		self.bridge = bridge
		self.accept_new_connections = True
		self.connections = []
		self.accept_new_connections_thread = False