from console.CAMERA import CAMERA
import pickle
from cryptography.fernet import Fernet
import time
import threading
from console.BRIDGE import BRIDGE

class CONNECTION:
	def hear(self):
		splitter = "~~~~~~".encode("utf-8")
		data = b""
		while self.listen:
			try:
				data += self.conn.recv(2048)
			except:
				self.messages.append(False)
				data = False
			if not data:
				break
			if splitter in data:
				for d in data.split(splitter):
					d = d.replace(splitter, b"")
					if len(d) > 10:
						self.messages.append(d)
				data = b""
		self.listen = False

	
	def logic(self):
		global data, settings, log
		bridge = BRIDGE(data, settings, self.camera)
		user = USER(bridge, pr=self.pr, camera=self.camera)
		user.log_in(user_id="Quest", password=False, inp=self.input_user, pr=self.pr)
		while self.listen:
			if user.logged:
				user.run_print(self.input_user, pr=self.pr)
			else:
				bridge = BRIDGE(data, settings, self.camera)
				user = USER(bridge, pr=self.pr)
				user.log_in(inp=self.input_user, pr=self.pr)

	def get_good_delay(self):
		i = 0
		while not self.check_secure():
			self.delay = self.delay * 2
			#print("Testing {}".format(i))
			i += 1
			if i == 20:
				print("Error connecting with secure connection with: ip: {} port: {}\nStopping connection".format(self.host, self.port))
				self.listen = False
				return False
		#print(self.delay)
		return True

	def read_camera(self):
		self.send_data("%%%INPUTCAMERA%%%", printt=False)

		readed = self.recv(pickle_m=True)

		if type(readed) == str:
			if "%%%NOCAMERA%%%" in readed:
				return False
			else:
				return False
		else:
			#cv2.imshow("img", readed)
			#cv2.waitKey(0)
			return readed
		#print(self.recv(pickle_m=True))

	def check_secure(self):
		self.send_data("SERVER IS GOING TO DO A TEST")
		self.send_data("SERVER IS GOING TO SEND A INPUT COMMAND")
		if not self.input_user("%%%SERVER_REPLY%%%") == "%%%CORRECT_REPLY%%%":
			return False
		return True

	def send_data(self, dat, printt=True):
		for a in str(dat).split("\n"):
			if printt:
				a = "%%%PRINT%%%" + a
			nd = str(a).encode("utf-8")
			#print("Sending: {}".format(nd))
			nd = self.fernet.encrypt(nd) + b"~~~~~~"
			try:
				self.conn.sendall(nd)
			except:
				self.listen = False
			time.sleep(self.delay)

	def pr(self, m, p="", n=""):
		self.send_data(str(m)+str(p)+str(n))

	def recv(self, pickle_m=False):
		try:
			i = 0
			while True:
				if len(self.messages) > 0:
					dat = self.messages[i]
					#print("Recv: {}".format(dat))
					dat = self.fernet.decrypt(dat)
					if not pickle_m:
						dat = dat.decode("utf-8")
					else:
						dat = pickle.loads(dat)
					del self.messages[i]
					#print("Decrypt: {}".format(dat))
					return dat
				time.sleep(0.01)
		except Exception as e:
			#print(e)
			self.listen = False
			return " "

	def input_user(self, message):
		self.send_data("%%%INPUT%%%" + message, printt=False)
		n = self.recv()
		#print("input: {}".format(n))
		return n 

	def setup_camera(self):
		self.camera = CAMERA(self.read_camera)

	def test_camera(self, info=True):
		if self.test_camera_:
			#print("Testing camera")
			res = self.read_camera()
			f = False
			try:
				if res:
					f = True
			except:
				f = True

			if not info:
				return f

			if f:
				#print("Found camera")
				self.pr("Found camera")
			
			return f

	def setup(self):
		self.ht = threading.Thread(target=self.hear)
		self.ht.start()

		if self.test_camera():
			self.setup_camera()

		if self.get_good_delay():
			self.hear_thread = threading.Thread(target=self.logic)
			self.hear_thread.start()

	def __init__(self, conn, addr):
		self.host = addr[0]
		self.port = addr[1]
		self.conn = conn
		self.listen = True
		self.test_camera_ = True
		self.camera = False
		self.messages = []
		self.delay = 0.0001
		self.key = "VlD8h2tEiJkQpKKnDNKnu8ya2fpIBMOo5oc7JKNasvk="
		self.fernet = Fernet(self.key)
		self.st = threading.Thread(target=self.setup)
		self.st.start()