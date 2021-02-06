import time
import json

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