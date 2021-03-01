import json

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
			open(self.directory+self.settings_file_name, "w").write(settings_raw)
		except:
			print("Error saving settings")
		else:
			self.p("Saved")

	def load_settings(self):
		self.p("Loading settings")

		try:
			settings_raw = open(self.directory+self.settings_file_name, "r").read()
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
			self.data_file_name = self.dirr(sett["data_file_name"])
			self.log_file_name = self.dirr(sett["log_file_name"])
			#self.log = sett["log"]

			return changed
	def dirr(self, name):
		if name:
			name = self.directory + name
		return name

	def p(self, m, p="SETTINGS"):
		if self.log:
			print("{}:{}".format(p, m))

	def __init__(self, log=False):
		self.directory = "data/"
		self.settings_file_name = "settings.json"
		self.extension = ".json"
		self.data_file_name = "data."
		self.log_file_name = "log."
		self.log = log
		self.change_extension()
		if self.load_settings():
			self.change_extension()
			self.change_file_name()