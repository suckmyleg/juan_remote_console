
class BRIDGE:
	def load_clients(self):
		clients = [["twitch_clips", "twitch_clips_client.py"]]
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
				else:
					print("Stopped client: {}".format(c[0]))


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

	def get_user_id_camera(self, camera, pr=print, inp=input):
		try:
			data = self.data.rec.who(min=3, camera=camera)
			user_id = data[0][1]
			return user_id
		except Exception as e:
			return False

	def who(self, user_id, camera, pr=print, inp=input):
		pr(self.get_user_id_camera(camera, pr=pr, inp=input))

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