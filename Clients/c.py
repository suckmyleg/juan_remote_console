from time import sleep
import json
from threading import Thread as th
import socket

class SEND_RECV:
	def stop(self):
		self.recv_messages = False

	def send_command(self, command, message=False, message1=False, message2=False, message3=False, message4=False, message5=False):
		if not message:
			message = ""

		message = self.command_decor + command + str(message)

		if message1:
			message += str(message1)

		if message2:
			message += str(message2)

		if message3:
			message += str(message3)

		if message4:
			message += str(message4)

		if message5:
			message += str(message5)

		self.send(message)

	def inp(self, message=False, message1=False, message2=False, message3=False, message4=False, message5=False):
		self.send_command("INPUT", message, message1, message2, message3, message4, message5)

		return self.recv()

	def pr(self, message=False, message1=False, message2=False, message3=False, message4=False, message5=False):
		self.send_command("PRINT", message)

	def send(self, message):
		d = str(message).encode("utf-8")
		self.conn.sendall(self.send_data_slip_decor_byte + d + self.send_data_slip_decor_byte)

	def listen(self):
		for i in range(self.max_tries):
			while self.recv_messages:
				try:
					message = self.conn.recv(self.buffer)
				except:
					self.conn = False
					break
				while len(message.split(self.send_data_slip_decor_byte)) < 3:
					message += self.conn.recv(self.buffer)
				self.messages.append(message)
			if not self.recv_messages:
				break
				return ""
			if not self.connect():
				print("Connection lost trying to connect... ({}/{})".format(i, self.max_tries))
				sleep(1)
			else:
				print("Reconnected")

	def recv(self):
		while self.recv_messages:
			for m in self.messages:
				d = m.decode("utf-8").replace(self.send_data_slip_decor, "")
				del self.messages[self.messages.index(m)]
				return d
			sleep(self.delay)			

	def command_to_action(self, message):
		for c in self.react_commands:
			full = self.command_decor+c[0]
			if full in message:
				return c[1](message.replace(full, ""))

	def react(self):
		message = self.recv()
		ret = self.command_to_action(message)
		if not ret == None:
			self.send(ret)

	def connect(self):
		if not self.conn:
			self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if self.host and self.port:
				try:
					self.conn.connect((self.host, self.port))
				except:
					return False
				else:
					if not self.listen_thread:
						self.start()
				return True
			else:
				print("Host and port needed to connect")
				return False
		else:
			print("Already connected to host")
			return False

	def start(self):
		if not self.listen_thread:
			self.listen_thread = th(target=self.listen)
			self.listen_thread.start()
		else:
			print("Tried to start thread when its already started")

	def __init__(self, conn=False, host=False, port=False, buffer=2048, pr=print, inp=input):
		self.conn = conn
		self.host = host
		self.port = port
		self.messages = []
		self.delay = 0.01
		self.max_tries = 15
		self.recv_messages = True
		self.buffer = buffer

		self.command_decor = "$$$$$$$$$$$$$"

		self.listen_thread = False

		self.send_data_slip_decor = "%%%%%%%%%%%"
		self.send_data_slip_decor_byte = self.send_data_slip_decor.encode("utf-8")
		self.user_print = pr
		self.user_input = inp

		self.react_commands = [
		["INPUT", self.user_input],
		["PRINT", self.user_print]
		]

		if self.conn:
			self.start()
		else:
			if self.host and self.port:
				self.connect()


def start(pr=print, inp=input):

	host = "192.168.1.92"
	port = 5656

	s = SEND_RECV(host=host, port=port, pr=pr, inp=inp)

	while True:
		s.react()