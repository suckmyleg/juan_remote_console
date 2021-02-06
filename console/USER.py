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

			if self.bridge.data.user_credentials(user_id, password):
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