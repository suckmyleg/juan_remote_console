import os

from threading import Thread as th
import json
import time
import socket
import pickle


try:
	import numpy as np
except:
	print("Installing optional module")
	os.system("pip3 install numpy")
	os.system("pip install numpy")
	os.system("py -m pip install numpy")
	import numpy as np


try:
	import cv2
except:
	print("Installing optional module")
	os.system("pip3 install opencv-python")
	os.system("pip install opencv-python")
	os.system("py -m pip install opencv-python")
	import cv2

try:
	import webbrowser
except:
	print("Installing optional module")
	os.system("pip3 install webbrowser")
	os.system("pip install webbrowser")
	os.system("py -m pip install webbrowser")
	import webbrowser


"""
try:
	from cryptography.fernet import Fernet
except:
	print("Installing required modules")
	os.system("pip install cryptography")
	os.system("py -m pip install cryptography")
	try:
		from cryptography.fernet import Fernet
	except:
		print("Failed to install")
"""
class RECV_FILE_CONTENT:
	def __init__(self, name, size, bufferr, download_location, get_file_data, debug, times=False, auto=False, pr=print, inp=input):
		self.b = bufferr
		self.file_name = name
		self.file_size = size
		self.download_location = download_location
		self.get_file_data = get_file_data
		self.debug = debug
		self.times = times
		self.data = []
		self.auto = auto

		self.pr = pr
		self.inp = inp

		if self.debug:
			self.pr("file_name: {}\nfile_size: {}\nbuffer: {}".format(self.file_name, self.file_size, self.b))

		if not self.times:
			self.t = self.file_size / self.b
			if (self.file_size % self.b) > 0: self.t += 1
		else:
			self.t = self.times

		self.t = int(self.t)
		
		self.s = time.time()

		self.i = 0

		self.finished = False

		self.file = False

		self.incomplete_data = b""

		if self.auto:
			self.auto_thread = th(target=self.auto_)
			self.auto_thread.start()

	def stop(self):
		self.auto = False

	def recv_all(self):
		data = []
		for self.i in range(self.t):
			d = self.recv(m=False)
			if d:
				data.append(d)
			else:
				return data
		return data

	def write(self):
		self.file = open(self.download_location + self.file_name, "wb")
		for self.i in range(self.t):
			d = self.recv(m=False)
			if d:
				self.file.write(d)
			else:
				break
		self.file.close()
		
	def r(self):
		while True:
			for d in self.data:
				del self.data[0]
				return d
			time.sleep(0.001)

	def auto_(self):
		while self.auto:
			data = self.recv()
			if data:
				self.data.append(data)
				#self.pr(len(data))
			else:
				self.data.append(False)
				break

	def recv(self, m=True):
		if not self.i == self.t-1:
			while True:
				self.incomplete_data += self.get_file_data(buffer=self.b)
				if time.time() - self.s > 1 or self.debug:
					self.pr("Downloaded: {}%".format(int((self.i*100)/self.t)))
					self.s = time.time()
				if self.debug:
					time.sleep(0.001)
				if len(self.incomplete_data) == self.b:
					data = self.incomplete_data
					self.incomplete_data = b""
					break
				else:
					if len(self.incomplete_data) > self.b:
						data = self.incomplete_data[:self.b]
						self.incomplete_data = self.incomplete_data[self.b:len(self.incomplete_data)]
						break
			if m:
				self.i += 1
			return data
		else:
			if not self.finished:
				self.pr("Finished downloading: {}".format(self.file_name))
				self.finished = True
				if self.file:
					self.file.close()
		return False
class CONNECTION:
	def __init__(self, host, port, pr=print, inp=input):
		self.host = host
		self.port = port

		self.pr = pr
		self.inp = inp

		self.send_messages = []

		self.version = "0.0.6"

		self.download_location = ""

		self.download_server_host = self.host
		self.download_server_port = self.port + 100

		self.buffer_size = 1024

		self.encrypted_messages = False

		self.debug = False

		self.videos = []

		self.delay_check_new_message = 0.001

		if self.debug:
			self.pr("Setting fernet key")

		self.key = "VlD8h2tEiJkQpKKnDNKnu8ya2fpIBMOo5oc7JKNasvk="

		try:
			if self.encrypted_messages:
				if self.debug:
					self.pr("Setting up fernet")
				#self.fernet = Fernet(self.key)
		except:
			self.pr("Error setting fernet key")
			self.inp()
		else:
			if self.debug:
				self.pr("Finished setting up fernet")

		self.messages = []
		self.commands = [
		["PRINT", self.pr],
		["INPUT", self.input],
		["RECV_FILE", self.recv_file_from_server],
		["RECV_VIDEO_STREAM", self.video_stream],
		["RECV_VIDEO_DOWNLOAD_FIRST", self.download_before],
		["VERSION", self.send_version],
		["OUTDATED", self.outdated],
		["OPEN_BROWSER", self.open_web],
		["SET_BUFFER_SIZE", self.set_buffer_size]]

	def set_buffer_size(self, arg):
		self.buffer_size = int(arg)

	def outdated(self, arg):
		self.pr("Old console version")
		self.pr("Last version: {}\nYour version: {}".format(arg, self.version))

	def open_web(self, arg):
		#arg = "http://" + arg.replace("juanmacaco2.ddns.net:9999", "192.168.1.104")
		webbrowser.get('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s').open(arg)
		webbrowser.get('C:/Program Files/Google/Chrome/Application/chrome.exe %s').open(arg)

	def send_version(self, arg):
		self.send(self.version)

	def send(self, msg):
		i = str(msg)
		if len(i) < 1:
			i = " "
		if self.debug:
			self.pr("Send: ({})".format(i))
		if self.encrypted_messages:
			pass
			#i = self.fernet.encrypt(i.encode("utf-8"))
		else:
			i = i.encode("utf-8")
		self.conn.sendall(i)

	def connect_transfer_file_server(self):
		self.download_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if self.debug:
			self.pr("Connecting to transfer_file server")
		self.download_server.connect((self.download_server_host, self.download_server_port))
		if self.debug:
			self.pr("Connected")
		return True

	def play_video(self, frames):
		while True:
			i = 0
			for d in frames:
				i += 1
				l = len(frames)
				if self.debug:
					self.pr("Frame {}/{}".format(i, l))
				cv2.imshow("clip", d)
				if cv2.waitKey(10) & 0xFF == ord('q'):
					break
			cv2.destroyAllWindows()
			if "n" in str(self.inp("Rewatch? Y/n")).lower():
				break

	def download_before(self, data):
		file, typ = data.split("%%%")
		if self.connect_transfer_file_server():
			if self.debug:
				self.pr("Send: ({})".format("STREAM_FALSE"))
			self.download_server.sendall("{}%%{}%%{}".format("STREAM_FALSE", file, typ).encode("utf-8"))
			n_frames = int(self.download_server.recv(1024).decode("utf-8"))
			already_downloaded = False
			for v in self.videos:
				if v[0] == file:
					if len(v[1]) == n_frames:
						self.play_video(v[1])
						already_downloaded = True
					else:
						self.pr("Video corrupted, downloading again")
			if not already_downloaded:
				if self.debug:
					self.pr("n_frames: {}".format(n_frames))
				buffer_ = int(self.download_server.recv(1024).decode("utf-8"))
				if self.debug:
					self.pr("buffer_: {}".format(buffer_))
				self.recv_file_object = RECV_FILE_CONTENT(file, False, buffer_, self.download_location, self.get_file_data, debug=self.debug, times=n_frames, auto=False)
				self.pr("Reading frames...")
				bframes = self.recv_file_object.recv_all()
				frames = []
				for f in bframes:
					frames.append(pickle.loads(f))
				if self.debug:
					self.pr("Showing video from already data downloaded")
				self.videos.append([file, frames])
				if "n" in str(self.inp("Rewatch? Y/n")).lower():
					return ""
				self.play_video(frames)

	def video_stream(self, data):
		file, typ = data.split("%%%")
		if self.connect_transfer_file_server():
			if self.debug:
				self.pr("Send: ({})".format("STREAM"))
			self.download_server.sendall("{}%%{}%%{}".format("STREAM", file, typ).encode("utf-8"))
			n_frames = int(self.download_server.recv(1024).decode("utf-8"))
			already_downloaded = False
			for v in self.videos:
				if v[0] == file:
					if len(v[1]) == n_frames:
						self.play_video(v[1])
						already_downloaded = True
					else:
						self.pr("Video corrupted, downloading again")
			if not already_downloaded:
				if self.debug:
					self.pr("n_frames: {}".format(n_frames))
				buffer_ = int(self.download_server.recv(1024).decode("utf-8"))
				if self.debug:
					self.pr("buffer_: {}".format(buffer_))
				self.recv_file_object = RECV_FILE_CONTENT(file, False, buffer_, self.download_location, self.get_file_data, debug=self.debug, times=n_frames, auto=True)
				data = self.recv_file_object.r()
				if self.debug:
					self.pr("Showing video while downloading")
				ret = True
				frames = []
				while data:
					try:
						frame = pickle.loads(data)
						ret = True
					except:
						ret = False
					else:
						frames.append(frame)
						if ret:
							cv2.imshow("clip", frame)
						if cv2.waitKey(1) & 0xFF == ord('q'):
							break
					data = self.recv_file_object.r()
				self.recv_file_object.stop()
				if self.debug:
					self.pr("Destroying all windows")
				cv2.destroyAllWindows()
				if self.debug:
					self.pr("Showing video from already data downloaded")
				self.videos.append([file, frames])
				if "n" in str(self.inp("Rewatch? Y/n")).lower():
					return ""
				self.play_video(frames)
			

	def recv_file_from_server(self, data):
		file, typ = data.split("%%%")
		if not os.path.isfile(self.download_location + file):
			self.connect_transfer_file_server()
			if self.debug:
				self.pr("Send: ({})".format(file))
			self.download_server.sendall("{}%%{}%%{}".format("DOWNLOAD", file, typ).encode("utf-8"))
			size = int(self.download_server.recv(1024).decode("utf-8"))
			self.recv_file_object = RECV_FILE_CONTENT(file, size, 1024, self.download_location, self.get_file_data, debug=self.debug)
			self.recv_file_object.write()
		else:
			self.pr("Video already downloaded")
	
	def auto_send(self, messages):
		self.send_messages.append(messages)

	def get_file_data(self, buffer=1024):
		return self.download_server.recv(buffer)

	def input(self, msg):
		if len(self.send_messages) > 0:
			if len(self.send_messages[0]) > 0:
				m = self.send_messages[0][0]
				self.pr("{}{}".format(msg, m))
				self.send(m)
				del self.send_messages[0][0]
			if len(self.send_messages[0]) == 0:
				del self.send_messages[0]
		else:
			i = self.inp(msg)
			self.send(i)

	def start(self):
		self.hear = True
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if self.debug:
			self.pr("Connecting with server {}:{}".format(self.host, self.port))
		try:
			self.conn.connect((self.host, self.port))
		except:
			self.pr("Error connecting to the server")
			return False
		if self.debug:
			self.pr("Connected\nListening")
		self.listen_thread = th(target=self.listen)
		self.listen_thread.start()
		return True

	def recv(self):
		while True:
			for m in self.messages:
				data = m
				del self.messages[self.messages.index(m)]
				if self.encrypted_messages:
					pass
					#data = self.fernet.decrypt(data.encode("utf-8")).decode("utf-8")
				if self.debug:
					self.pr("Recv: ({})".format(data))
				return data
			time.sleep(self.delay_check_new_message)

	def main(self):
		if self.start():
			if self.debug:
				self.pr("Main function started")
			while True:
				data = self.recv()
				for c in self.commands:
					if c[0] in data:
						data = data.replace("%%%"+c[0]+"%%%", "")
						c[1](data)
		else:
			self.inp()
			return ""

	def listen(self):
		while self.hear:
			data = self.conn.recv(self.buffer_size).decode("utf-8")
			l = data.split("ªªªªª")
			for i in range(len(l)-1):
				m = l[i]
				self.messages.append(m)

def start(pr=print, inp=input):
	c = CONNECTION("192.168.1.104", 4444, pr=pr, inp=inp)

	c.main()

if __name__ == "__main__":
	start()