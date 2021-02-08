import threading
import json
import time
import os
import sys
import rec
from cryptography.fernet import Fernet
import socket
import pickle
import cv2

class SETTINGS:
	def change_file_name(self, data_file_name=False, log_file_name=False):
		self.p("Changing file names")
		if data_file_name:
			self.p("New data file name found")
			self.data_file_name = data_file_name
		if log_file_name:
			self.p("New log file name found")
			self.log_file_name = log_file_name
			print(self.data_file_name)
		self.data_location = "" + self.data_file_name
		self.log_location = "" + self.log_file_name

	def change_extension(self, extension=False):
		self.p("Changing extension")
		if extension:
			self.p("New extension found")
			self.extension = extension
		self.data_file_name = self.data_file_name.split(".")[0] + self.extension
		self.log_file_name = self.log_file_name.split(".")[0]  + self.extension
		self.change_file_name()

	def save_settings(self):
		self.p("Saving settings")
		sett = {"extension":self.extension, "data_file_name":self.data_file_name, "log_file_name":self.log_file_name, "log":self.log}
		settings_raw = json.dumps(sett, indent=5)
		try:
			open(self.settings_file_name, "w").write(settings_raw)
		except:
			print("Error saving settings")
		else:
			self.p("Saved")

	def load_settings(self):
		self.p("Loading settings")

		try:
			settings_raw = open(self.settings_file_name, "r").read()
		except:
			self.save_settings()
		else:
			self.p("Loaded")

			sett = json.loads(settings_raw)

			changed = False

			array_settings = [[self.extension, sett["extension"]], [self.data_file_name, sett["data_file_name"]], [self.log_file_name, sett["log_file_name"]], [self.log, sett["log"]]]

			for a in array_settings:
				if not a[0] == a[1]:
					changed = True
					break

			self.extension = sett["extension"]
			self.data_file_name = sett["data_file_name"]
			self.log_file_name = sett["log_file_name"]
			self.log = sett["log"]

			return changed

	def p(self, m, p="SETTINGS"):
		if self.log:
			print("{}:{}".format(p, m))

	def __init__(self):
		self.settings_file_name = "settings.json"
		self.extension = ".json"
		self.log = False
		self.data_file_name = "data."
		self.log_file_name = "log."
		self.change_extension()
		self.log = True
		if self.load_settings():
			self.change_extension()
			self.change_file_name()

class LOG:
	def add_entry(self, caller, entry):
		user = False

		try:
			user = self.log["users"][caller]
		except:
			pass

		if not user:
			user = self.log["users"][caller] = {"logged":0, "logs":[], "last_logged":time.time()}

		user["logs"].append(entry)
		user["logged"] += 1
		user["last_logged"] = time.time()

		self.log["users"][caller] = user

		#self.save() 

	def p(self, m):
		self.settings.p(m, p="LOG")

	def load(self):
		try:
			raw_log = open(self.settings.log_location, "r").read()
		except:
			if not self.save():
				self.p("Error loading log")
		else:
			self.log = json.loads(raw_log)
			self.p("Loaded log")

	def save(self):
		raw_log = json.dumps(self.log, indent=5)

		try:
			open(self.settings.log_location, "w").write(raw_log)
		except:
			self.p("Error trying to save log")
			return False
		else:
			return True

	def __init__(self, settings):
		self.settings = settings
		self.log = {"users":{}}
		self.load()

class DATA:
	def l(self, caller, args, target="", pr=print, inp=input):
		targets = target.split(" ")
		k = ""
		for g in targets:
			k+= "_"+str(g)
		self.log.add_entry("DATA", {"caller":str(caller), "time":time.time(), "action":{"target":target, "args":args, "command":str(type).lower()+k}})

	def d(self, caller, pr=print, inp=input):
		self.l(caller, [], "data")
		return self.content

	def p(self, m):
		self.settings.p(m, p="DATA")

	def set_permission_level_action(self, caller, action_str, permission_level, pr=print, inp=input):
		try:
			p = self.content["actions"][action_str]
		except:
			pr("Action '{}' doesnt exists".format(action_str))
			self.ae("set_permission_level_action", "Action '{}' doesnt exists".format(action_str))
		else:
			self.content["actions"][action_str]["permission_level"] = permission_level
			self.save()

	def add_action(self, caller, action_str, permission_level, pr=print, inp=input):
		try:
			p = self.content["actions"][action_str]
		except:
			self.content["actions"][action_str] = {"permission_level":permission_level}
			self.save()
		else:
			pr("Action '{}' already exists".format(action_str))
			self.ae("add_action", "Action '{}' already exists".format(action_str))

	def save(self, user_id=False, pr=print, inp=input):
		if self.fernet:
			self.raw = json.dumps(self.content, indent=5)
			self.bytes_data = str(self.raw).encode("utf-8")
			try:
				self.encrypted_data = self.fernet.encrypt(self.bytes_data)
			except Exception as e:
				pr("Error encrypting the data\n", e)
				self.ae("permission", "Error encrypting the data")
				return False

			try:
				open(self.settings.data_location, "wb").write(self.encrypted_data)
			except:
				pr("Error saving the data")
				self.ae("save", "Error saving the data")
		else:
			pr("Saved skipped")
			self.ae("save", "Save skipped fernet not working")

	def permission(self, caller, user, action, say=True, pr=print, inp=input):
		users = self.users_list(caller)
		exists = False
		for u in users:
			if u["user_id"] == user:
				exists = True
				break
		if exists:
			user_data = self.get_user_data(caller, user, check_permission=False)
			level = self.get_permission_level(caller, action)
			#print("if {} >= {}".format(level, user_data["permission_level"], level)) 
			if level:
				if int(user_data["permission_level"]) >= level:
					return True
				else:
					if say:
						pr("Access denied")
					self.ae("permission", "Access denied to caller: {}".format(caller))
					return False
			else:
				if say:
					pr("Action '{}' doesn't exist\nDenied by default.".format(action))
				self.ae("permission", "Action '{}' doesn't exist\nDenied by default. Caller {}".format(action, caller))
				return False

	def get_permission_level(self, caller, action, pr=print, inp=input):
		#self.l(caller, [], "permission level action")
		try:
			level = int(self.content["actions"][action]["permission_level"])
		except:
			return False
		else:
			return level

	def set_permission_level_user(self, caller, user, permission_level, pr=print, inp=input):
		#self.l(caller, [], "permission level user")
		try:
			p = self.content["users"]["content"][user]
		except:
			pr("User '{}' doesnt exists".format(action_str))
			self.ae("set_permission_level_user", "User '{}' doesnt exists".format(action_str))
		else:
			self.content["users"]["content"][user]["permission_level"] = int(permission_level)
			self.save()

	def rename_user(self, caller, user, new_name, pr=print, inp=input):
		self.save()
		try:
			p = self.content["users"]["content"][user]
			del self.content["users"]["content"][user]
			self.content["users"]["content"][new_name] = p
			newlist = self.users_list(caller, pr=pr, inp=input)
			for u in newlist:
				if str(u["user_id"]) == user:
					u["user_id"] = new_name
			self.content["users"]["list"] = newlist
		except Exception as e:
			pr("User '{}' doesnt exists".format(user))
			self.ae("rename_user", "User '{}' doesnt exists".format(user))
			self.load()
		else:
			self.save()

	def get_user_data(self, caller, user, check_permission=True, pr=print, inp=input):
		user = str(user)
		permission = False
		if check_permission:
			if self.permission(self.user_id, caller, "get_user_data"):
				permission = True
		else:
			permission = True
		if permission:
			self.l(caller, [user], "user data")
			try:
				user = self.content["users"]["content"][user]
			except:
				return False
			else:
				return user
		else:
			return False

	def users_list(self, caller, pr=print, inp=input):
		self.l(caller, [], "users list")
		return self.content["users"]["list"]

	def ae(self, m, e):
		self.errors.append([m, e])

	def load(self, user_id=False, pr=print, inp=input):
		if self.fernet:
			try:
				self.encrypted_data = open(self.settings.data_location, "rb").read()
			except:
				self.save()

			try:
				self.bytes_data = self.fernet.decrypt(self.encrypted_data)
			except:
				pr("Error decrypting the data")
				self.ae("load", "Error decrypting the data")
				return False

			try:
				self.raw = self.bytes_data.decode("utf-8")
			except:
				pr("Error decoding the data")
				çself.ae("load", "Error decoding the data")
			try:
				self.content = json.loads(self.raw)
			except:
				pr("Error loading data")
				self.ae("load", "Error loading the data")
		else:
			pr("\nLoad skipped\nThe console has no data due to issues loading the encrypt key\nLoading default data")
			self.ae("load", "Fernet not loaded")

	def user_credentials(self, user_id, password, pr=print, inp=input):
		dat = self.get_user_data(self.user_id, user_id)
		
		if not dat:
			return False

		if not dat["password"] or dat["password"] == password:
			return True
		else:
			return False

	def user_logged(self, caller_id, user_id, pr=print, inp=input):
		pass

	def display_errors(self, caller, pr=print, inp=input):
		info = [self.key]
		for e in self.errors:
			pr("{}> {}".format(e[0], e[1]))
		for r in info:
			pr("{}> {}".format("Info", r))

	def __init__(self, settings, log, rec):
		self.user_id = "0" 
		self.settings = settings
		self.log = log
		self.rec = rec
		self.raw = ""
		self.key = "VlD8h2tEiJkQpKKnDNKnu8ya2fpIBMOo5oc7JKNasvk="
		self.errors = []
		self.content = {"users":{"list":[], "content":{}}, "actions":{}}
		try:
			self.fernet = Fernet(self.key)
		except:
			print("Encrypt module failed loading the key")
			self.ae("Main", "Not valid kernet key")
			self.encrypted_data = ""
			self.bytes_data = b""
			self.raw = ""
			self.content = {"users":{"list":[{"user_id":"User-temporal-worker"}, {"user_id":"0"}], "content":{"User-temporal-worker":{"permission_level":5, "password":"worker-password"}, "0":{"permission_level":20, "password":"woooooooooooooooooopapappapa"}}}, "actions":{"get_users_list":{"permission_level":1},"get_data":{"permission_level":10},"get_permission_level_action":{"permission_level":1},"get_user_data":{"permission_level":10},"get_permission_level":{"permission_level":"2"},"help":{"permission_level":1},"logout":{"permission_level":1},"permission":{"permission_level":1},"save_data":{"permission_level":1},"load_data":{"permission_level":1},"add_action":{"permission_level":"5"},"set_permission_level_action":{"permission_level":"10"},"set_permission_level_user":{"permission_level":"10"},"users_list":{"permission_level":"2"},"error":{"permission_level":"1"}}}
			self.fernet = False
		else:
			self.load()

class BRIDGE:
	def load_clients(self):
		clients = [["twitch_clips", "twitch_clips_client.py"], ["discord", "c.py"]]
		self.clients = []
		for c in clients:
			try:
				function = __import__("Clients."+c[1].replace(".py", ""), fromlist=['start'])
				self.clients.append([c[0], function.start])
			except Exception as e:
				print("Error importing client: {}".format(c[0]), e)

	def connect_to_client(self, user_id, client_name, pr=print, inp=input):
		for c in self.clients:
			if client_name == c[0]:
				try:
					c[1](pr, inp)
				except:
					print("Error running client: {}".format(c[0]))
					return False
				else:
					print("Stopped client: {}".format(c[0]))
					return True

		print("Not found client")


	def __init__(self, data, settings, camera):
		self.data = data
		self.settings = settings
		self.camera = camera
		if self.data.fernet:
			try:
				self.commands = [
				[self.data.d, "get_data"],
				[self.data.permission, "permission"], 
				[self.data.get_permission_level, "get_permission_level"], 
				[self.data.get_user_data, "get_user_data"], 
				[self.data.users_list, "users_list"],
				[self.data.save, "save_data"],
				[self.data.load, "load_data"],
				[self.data.add_action, "add_action"],
				[self.data.set_permission_level_action, "set_permission_level_action"],
				[self.data.set_permission_level_user, "set_permission_level_user"],
				[self.data.rec.help, "rec_help"],
				[self.close_server, "close_server"],
				[self.data.rename_user, "rename"],
				[self.connect_to_client, "cc"]
				]
				self.user_commands = False
			except:
				print("Error trying to setup commands")
		else:
			self.commands = [
			[self.data.display_errors, "error"]]
			self.user_commands = False
		self.load_clients()



	def restart_server(self, user_id, pr=print, inp=input):
		pass

	def close_server(self, user_id, pr=print, inp=input):
		global server
		try:
			server.s.close()
		except Exception as e:
			pr("Error trying to close the server")
			pr(e)
			return False
		else:
			return True

	def help(self, user_id, only_runable=True, pr=print, inp=input):
		pr("\nCommands:")
		for c in self.commands:
			if not only_runable or self.data.permission(user_id, user_id, c[1], say=False):
				pr(" ", c[1])

		if self.user_commands:
			pr("\nUser_commands:")
			for c in self.user_commands:
				if not only_runable or True:
					pr(" ", c[1])

	def get_user_id_camera(self, pr=print, inp=input):
		try:
			data = self.data.rec.who(min=3, camera=self.camera)
			user_id = data[0][1]
			return user_id
		except Exception as e:
			return False

	def who(self, user_id, pr=print, inp=input):
		pr(self.get_user_id_camera(pr=pr, inp=input))

	def setup_user_commands(self, user):
		if not self.user_commands:
			self.user_commands = [
				[user.logout, "logout"],
				[self.help, "help"],
				[self.who, "who"]
				]

	def get_command_from_input(self, string):
		for c in self.commands+self.user_commands:
			if c[1] == string:
				return c[0]
		return False

	def run_command(self, str_command, user_id, user=False, args=[], pr=print, inp=input):
		if user:
			self.setup_user_commands(user)

		str_command = str_command.lower()
		c = self.get_command_from_input(str_command)
		if not c:
			pr("Uknown command: '{}' args: {}".format(str_command, ["user_id"]+args))
			return False
		self.data.l(user_id, [], str_command)

		try:
			if self.data.permission(self.data.user_id, user_id, str_command, pr=pr):
				if len(args) == 0:
					return c(user_id, pr=pr, inp=inp)
				if len(args) == 1:
					return c(user_id,  args[0], pr=pr, inp=inp)
				if len(args) == 2:
					return c(user_id, args[0], args[1], pr=pr, inp=inp)
				if len(args) == 3:
					return c(user_id, args[0], args[1], args[2], pr=pr, inp=inp)
				if len(args) == 4:
					return c(user_id, args[0], args[1], args[2], args[3], pr=pr, inp=inp)
				if len(args) == 5:
					return c(user_id, args[0], args[1], args[2], args[3], args[4], pr=pr, inp=inp)
				if len(args) == 6:
					return c(user_id, args[0], args[1], args[2], args[3], args[4], args[5], pr=pr, inp=inp)
				if len(args) == 7:
					return c(user_id, args[0], args[1], args[2], args[3], args[4], args[5], args[6], pr=pr, inp=inp)
				if len(args) == 8:
					return c(user_id, args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], pr=pr, inp=inp)
			else:
				return False
		except Exception as e:
			pr("Error running '{}' args: {}\nError: {}".format(str_command, ["user_id"]+args, e))
			self.user_commands = False
			return False
		else:
			self.user_commands = False




class CAMERA:
	def __init__(self, read_function):
		self.read_function = read_function
	
	def read(self):
		ret = True
		try:
			dat = self.read_function()
		except:
			ret = False
			dat = []
		return ret, dat


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
				print("Error connectin with secure connection with: ip: {} port: {}\nStopping connection".format(self.host, self.port))
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



class SERVER:
	def accept_connections(self):
		while self.accept_new_connections:
			conn, addr = self.s.accept()
			p = CONNECTION(conn, addr)
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

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.accept_new_connections = True
		self.connections = []
		self.accept_new_connections_thread = False


class USER:
	def __init__(self, bridge, pr=print, inp=input, camera=False):
		self.user_id = ""
		self.mode = 0
		self.logged = False
		self.bridge = bridge
		self.pr = pr
		self.camera = camera

	def logout(self, user_id, pr=print, inp=input):
		self.logged = False

	def run(self, inp=input, pr=print):
		if self.logged:
			m = inp("")

			words = m.split(" ")

			command = ""
			args = []
			for e in words:
				if command == "":
					command = e
				else:
					args.append(e)
			
			return self.bridge.run_command(command, self.user_id, self, args, pr=pr, inp=inp)
		else:
			pr("User not logged pls log in again")

	def run_print(self, inp=input, pr=print):
		m = self.run(inp, pr=self.pr)
		if not m == None:
			pr(m)

	def log_in(self, user_id=False, password="__NO__PASSWORD__", auto_user_id_photo=True, inp=input, pr=print):
		tries = 3
		extra = ""
		for i in range(tries):
			if not user_id or password == "__NO__PASSWORD__":
				pr("")
				pr("LOGIN")
				extra = " "
			if not user_id:
				if auto_user_id_photo:
					user_id = self.bridge.get_user_id_camera()
				if not auto_user_id_photo or not user_id:
					user_id = inp(" user_id:")
				user_id = str(user_id)
			if password == "__NO__PASSWORD__":
				password = inp(" password:")

			if bridge.data.user_credentials(user_id, password):
				self.user_id = user_id
				self.logged = True
				pr(str(extra) + "Logged as " + str(user_id))
				return True
			else:
				password = "__NO__PASSWORD__"
				if i == tries-1:
					pr(" Incorrect password or user_id")
					return False
				pr(" Incorrect password or user_id. Tries left: {}".format(tries - i-1))

		pr("")
		return False


server = SERVER("192.168.1.92", 7777)

server.setup()

settings = SETTINGS()

log = LOG(settings)

rec = rec.rec(log=True)

data = DATA(settings, log, rec)

bridge = BRIDGE(data, settings, False)

user = USER(bridge)

if data.fernet:
	user.log_in(user_id="Quest", password=False)
else:
	user.log_in(user_id="User-temporal-worker", password="worker-password")

try:
	while True:
		while user.logged:
			user.run_print()
		bridge = BRIDGE(data, settings, False)
		user = USER(bridge)
		user.log_in()

except Exception as e:
	print(e)