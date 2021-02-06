import time
import json

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
