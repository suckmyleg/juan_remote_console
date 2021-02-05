try:
	import cv2
	import glob
	import json
	import pickle
	import random
	import face_recognition
	import os
	from os import scandir
	from math import sqrt
	from numpy import array as arrayy
	from mss import mss
	from PIL import ImageGrab
	import sys
	import getopt
	import numpy
except Exception as e:
	print("Error\n {}".format(e))

class FACE:
	def near(self, face, limit=False):
		if not limit:
			limit = self.min_speed

		ww = abs(face.middle_vector_x - self.middle_vector_x)
		hh = abs(face.middle_vector_y - self.middle_vector_y)

		vector_value = sqrt(ww**2 + hh**2)

		if self.log:
			print("{} == Speed: {}".format(self.name, vector_value))

		if vector_value < self.min_speed:
			#print("Yes")
			self.vector_value = vector_value
			return True
		else:
			return False
			#print("No")

	def load_name(self):
		self.name = "No_name"
		for m in self.names:
			self.name = m
			break

	def get_name(self):
		reload_name = False
		if self.switch_names:
			limit = len(self.names) * self.delay_beetween_names

			if self.name_turn == limit + self.delay_beetween_names - 1:
				self.name_turn = 0
				reload_name = True

			#print(self.name_turn, self.delay_beetween_names)

			try:
				self.name = self.names[int(self.name_turn / self.delay_beetween_names - 1)]
			except:
				pass

			self.name_turn += 1

		return self.name, reload_name

	def same(self, face):
		if self.near(face):
			#print(self.x, self.y, self.w, self.h)
			self.x = face.x
			self.y = face.y
			self.w = face.w
			self.h = face.h
			self.middle_vector_x = (self.x + self.w)/2 
			self.middle_vector_y = (self.y + self.h)/2
			#print(self.x, self.y, self.w, self.h)
			return True
		else:
			#print("NNO")
			return False

	def __init__(self, d, private_id=False, names=[], log=False):
		self.private_id = private_id
		self.names = names
		self.name = ""
		self.x = d[0]
		self.y = d[1]
		self.w = d[2]
		self.h = d[3]

		self.middle_vector_x = (self.x + self.w)/2 
		self.middle_vector_y = (self.y + self.h)/2

		self.face_frame = []

		self.vector_value = 0

		self.min_speed = 20

		self.failed = 0
		
		self.log = log

		self.rectangle_color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

		self.name_turn = 0
		self.delay_beetween_names = 20
		self.switch_names = True

		self.load_name()
		



class private_user:
	def __init__(self, private_id, privates_ids_file, examples_folder, folder_recognition, names=[], log=False):
		self.privates_ids_file = privates_ids_file
		self.private_id = private_id
		self.names = names
		self.file_recognition = "f" + str(private_id) + "data"
		self.folder_recognition = folder_recognition
		self.examples_folder = examples_folder
		self.user_encodings = []
		self.highest_boxes = 0
		self.log = log

	#GET PRIVATE ID FROM NAMES SUPPLIED
	def get_private_id(self, name):
		data = self.get_privates_ids()

		for d in data:
			if name in d["names"]:
				self.private_id = d["private_id"] 
				self.names = d["names"]
				self.file_recognition = d["file_recognition"]

	#GET DATA SAVED FROM PRIVATE ID
	def load_data(self):
		data = self.get_privates_ids()

		if self.log:
			print("{}: Loading data".format(self.private_id))

		for d in data:
			#print(d)
			if d["private_id"] == self.private_id:
				self.names = d["names"]
				self.file_recognition = d["file_recognition"]
				self.user_encodings = self.load_encodeds_face()
				#print(self.user_encodings, self.load_encodeds_face())

		if self.private_id:
			if not len(self.user_encodings) > 0:
				if self.log:
					print(" -----No Encodings\n")

	#GET THE NAMES FROM A PRIVATE ID
	def load_names(self):
		data = self.get_privates_ids()

		for d in data:
			if d["private_id"] == self.private_id:
				self.names = d["names"]
		

	#GET ALL THE PRIVATE IDS FROM FILE
	def get_privates_ids(self):
		try:
			data = json.loads(open(self.privates_ids_file, "r").read())
		except Exception as e:
			data = []
		return data


	def save(self):
		json_data = {"private_id":self.private_id, "file_recognition":self.file_recognition, "names":self.names}

		data = self.get_privates_ids()

		exists = False
		for d in data:
			if d["private_id"] == self.private_id:
				d = json_data
				exists = True

		if not exists:
			data.append(json_data)

		self.save_privates_ids(data)


	#SAVE PRIVATES IDS FILE
	def save_privates_ids(self, privates_ids):
		try:
			open(self.privates_ids_file, "w").write(json.dumps(privates_ids))
		except Exception as e:
			if self.log:
				print("Error saving privates_ids")
				print(e)


	def load_encodeds_face(self):
		try:
			dat = open(self.folder_recognition + self.file_recognition, "rb").read()
			try:
				content = pickle.loads(dat)
			except:
				content = []
			return content
		except Exception as e:
			if self.log:
				print(e)
			return []


	def save_encoded_face(self, encodes, n):
		try:
			self.user_encodings += encodes
			open(self.folder_recognition + self.file_recognition, "wb").write(pickle.dumps(self.user_encodings))
		except Exception as e:
			if self.log:
				print("Error trying to save encoded_face")
				print(e)
		else:
			if self.log:
				print("  -added face n{}".format(n))

	def record_frame(self, frame, log=False):
		boxes = face_recognition.face_locations(frame)

		encodings = face_recognition.face_encodings(frame, boxes)

		n = len(boxes)

		nl = len(self.user_encodings)

		if n > 1:
			if log:
				print("Multiple faces detected. Skipped")
		else:
			if log:
				print("Boxes: {}\nEncoding: {}+{}\n".format(n, nl, len(encodings)))

			di = self.examples_folder + str(self.private_id) + "/"

			name = str(nl) + ".jpg"

			if not os.path.isdir(di):
				os.mkdir(di)

			print(len(boxes) )

			if len(boxes) == 1:

				t, r, b, l = boxes[0]

				cv2.imwrite(di + name, frame[t:b, l:r])
			
			self.save_encoded_face(encodings, n=n)

	def save_face(self, image, log=False):
		frame = cv2.imread(image)

		self.record_frame(frame, log=log)

	def recogn_frame(self, frame, encodings, mode=0):
		for encoding in encodings:
			match = face_recognition.compare_faces(self.user_encodings, encoding)

			nm = 0

			for e in match:
				if e:
					nm += 1

			lue = len(self.user_encodings)

			if lue > 0:
				porc = (nm * 100)/lue
			else:
				porc = 0

			if mode == 0:
				return nm, porc


		return False




class rec:
	#GET NEW RANDOM PRIVATE ID
	def get_new_private_id(self):
		while True:
			new_private_id = random.randint(0, 9999999)

			data = self.get_privates_ids()

			unique = True
			for d in data:
				if d["private_id"] == new_private_id:
					unique = False
					break

			if unique:
				return new_private_id

	def new_user(self, name=False, private_id=False):
		names = []
		if not private_id:
			private_id = self.get_new_private_id()
		if name:
			names = [name]
		new = private_user(private_id, self.privates_ids_file, self.examples_folder, self.folder_recognition, names=names)

		new.save()

		self.users.append(new)

		return private_id, new


	def reload_users(self):
		for u in self.users:
			u.load_data()

	def reload_names(self):
		self.load_names_delay -= 1

		#print(self.load_names_delay)

		if self.load_names_delay <= 0: 

			for u in self.users:
				u.load_names()

			self.load_names_delay = 20

	def get_privates_ids(self):
		try:
			data = json.loads(open(self.privates_ids_file, "r").read())
		except:
			data = []
		return data

	def get_names(self, private_id):
		for u in self.users:
			if u.private_id == private_id:
				return u.names
		return []


	def get_users(self):
		data = self.get_privates_ids()

		if self.log:
			print("Gettings users")

		self.users = []

		for d in data:
			user = private_user(d["private_id"], self.privates_ids_file, self.examples_folder, self.folder_recognition, d["names"])
			user.load_data()
			if len(user.user_encodings) >= self.minimun_decoded:
				self.users.append(user)
			else:
				if self.log:
					print("User doesnt reach minimum_decoded, skipped. MoreNeeded: {}".format(self.minimun_decoded - len(user.user_encodings)))
	

	def recogn_all_frame(self, frame):
		privates_ids = []

		encodings = face_recognition.face_encodings(frame)

		for e in encodings:
			privates_ids.append(self.recogn_frame(frame, encodings=encodings))

		return privates_ids

	def higher(self, array):
		higher = [0]

		for a in array:
			if a[0] >  higher[0]:
				higher = a

		del array[array.index(higher)]
		return higher, array

	def short(self, array):
		shorted_array = []
		for a in range(len(array)):
			higher, array = self.higher(array)
			shorted_array.append(higher)
		return shorted_array 


	def pos(self, array, e):
		a = 0
		for i in array:
			for p in i:
				if p == e:
					return a
			a += 1

	def recogn_frame(self, frame, encodings=False):
		self.reload_names()

		higher_porc = []
		higher_match = []
		privates_ids = []

		if not encodings:
			encodings = face_recognition.face_encodings(frame)

		if len(encodings) == 0:
			return self.no_one_on_sreen

		i = 0

		for u in self.users:
			match, porc = u.recogn_frame(frame, encodings, self.mode)

			if match > 0 and porc > 0:

				higher_porc.append([porc, i])
				higher_match.append([match, i])
				privates_ids.append([u.private_id, i])
				i += 1

		higher_porc = self.short(higher_porc)
		higher_match = self.short(higher_match)

		top = [0, False]

		for i in privates_ids:
			por_i = self.pos(higher_porc, i[1])
			nat_i = self.pos(higher_match, i[1])
			dat = [por_i + nat_i, i[0], higher_porc[por_i][0], higher_match[nat_i][0]]

			if not top[1]:
				if self.proc_minim and dat[2] > self.minim_porc or not self.proc_minim:
					top = dat
			else:
				#print("{} > {} and ({} and {} > {} or not  {})".format(dat[0], top[0], self.proc_minim, dat[2], self.porc, self.proc_minim))

				if dat[0] < top[0] and (self.proc_minim and dat[2] > self.minim_porc or not self.proc_minim):
					top = dat 


		return top[1]





	def recogn_info_frame(self, frame):
		private_ids = []

		private_ids = self.recogn_all_frame(frame)

		if not private_ids:
			if self.log:
				print("Uknown")
			#self.record_face_from_webcam(webcam)
		else:
			if private_ids == self.no_one_on_sreen:
				if self.log:
					print("No one on screen")
			else:
				for private_id in private_ids:
					if self.log:
						print("private_id: {} --- names: {}".format(private_id, self.get_names(private_id)))

	def random_color(self):
		return (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255))

	def get_faces(self, frame):
		return self.pedestrian_face_tracker.detectMultiScale(frame)

	def display_frame_faces(self, frame, showvideo=False, showexample=False, showname=True, showrectangle=False, display_uknown=True, resize=False, returnframe=False, wk=1, reverse=False, track=True):
		try:
			rawfaces = self.get_faces(frame)

			if reverse:
				for r in rawfaces:
					f = []
					#f = frame[r[1]:r[1]+r[3], r[0]:r[0]+r[2]]
					#f = numpy.flip(f)
					frame[t:b, l:r] = f

			if track:
				self.display_frame_faces_oldfaces = self.track(self.display_frame_faces_oldfaces, rawfaces, frame)

			for o in self.display_frame_faces_oldfaces:
				name, o = self.get_face_name(o)

				if not name == "No_name" or display_uknown:

					if showname:
						cv2.putText(frame, name, (o.x, o.y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.random_color(), 2)

					if showrectangle:
						cv2.rectangle(frame, (o.x, o.y), (o.x+o.w, o.y+o.h), o.rectangle_color, 2)

			if resize:
				frame = cv2.resize(frame, (self.resolution_width, self.resolution_height), interpolation=cv2.INTER_NEAREST)
			
			if showvideo:
				cv2.imshow("output", frame)

			if showvideo and cv2.waitKey(wk) & 0xFF == ord("q"):
				return False
				cv2.destroyAllWindows() 
			else:
				if cv2.waitKey(wk) & 0xFF == ord("k"):
					while True:
						if cv2.waitKey(wk) & 0xFF == ord("l"):
							break
			if returnframe:
				return frame
			else:
				return True
		except:
			return True

	def get_face_name(self, face):
		name, reload = face.get_name()

		name = self.decore_name(name)

		if reload:
			self.reload_names()
			face.names = self.get_names(face.private_id)

		return name, face

	def decore_name(self, name):
		name = str(name).replace("&", str(random.randint(0, 9)))
		name = str(name).replace("%", str(random.randint(0, 9)))
		name = str(name).replace("$", str(random.randint(0, 9)))
		name = str(name).replace("#", str(random.randint(0, 9)))
		return name

	def get_name(self, private_id):
		try:
			for n in self.get_names(private_id):
				return self.decore_name(n)
			return "No name"
		except:
			return "No name"


	def create_new_faces(self, rawfaces):
		newfaces = []
		for n in rawfaces:
			new_face = FACE(n)
			newfaces.append(new_face)
		return newfaces



	def move_faces(self, faces, oldfaces):
		for p in oldfaces:
			moved = False
			for new_face in faces:
				if p.same(new_face):
					del faces[faces.index(new_face)]
					moved = True
			if not moved:
				del oldfaces[oldfaces.index(p)]
		return oldfaces + faces


	def track(self, oldfaces, rawfaces, frame):
		newfaces = self.create_new_faces(rawfaces)

		newfaces = self.move_faces(newfaces, oldfaces)

		faces = self.setup_new_faces(newfaces, frame)

		return faces
	
	def setup_new_faces(self, faces, frame, recogn=True):
		for n in faces:
			if not n.private_id:
				face_frame = frame[n.y:n.y+n.h, n.x:n.x+n.w]
				if recogn:
					private_id = self.recogn_frame(face_frame)
				else:
					private_id = 000000
				if private_id or not recogn:
					if not private_id == self.no_one_on_sreen and not private_id == []:
						n.private_id = private_id
						if recogn:
							n.names = self.get_names(private_id)
						else:
							n.names = ["Face"]
						n.load_name()
						n.face_frame = face_frame
					else:
						del faces[faces.index(n)]
				else:
					del faces[faces.index(n)]

		return faces









	#TOOLS READY TO DO STUFF WITHOUT NEED TO READ THE CODE
	#THESE TOOLS ARE FOR USE OF THE USER AND NOT FOR THE CODE

	def frame_faces_json(self, frame):

		rawfaces = self.get_faces(frame)

		self.display_frame_faces_oldfaces = self.track(self.display_frame_faces_oldfaces, rawfaces, frame)

		datas = []

		for f in self.display_frame_faces_oldfaces:
			datas.append({"private_id":f.private_id, "name":f.name, "names":f.names, "face":[int(f.x), int(f.y), int(f.w), int(f.h)], "speed":int(f.vector_value), "color":[f.rectangle_color[0], f.rectangle_color[1], f.rectangle_color[2]]})

		text_data = json.dumps(datas)

		return text_data


	#SAVES FACES FROM DIRECTORY, IF USER DOESNT EXISTS NEW USER IS CREATED AND IMAGES ARE SAVED TO HIS ENCODE FILE
	def images_new_needed_dir(self, directory, private_id=False):
		images = glob.glob(str(directory) + "/*.jpg") + glob.glob(str(directory) + "/*.png") + glob.glob(str(directory) + "/*.jpeg")
		if len(images) > 0:
			user = False
			if private_id:
				for u in self.users:
					if u.private_id == private_id:
						user = u
						if self.log:
							print("User found")
						break


			if not user:
				if self.log:
					print("User not found, creating new user. Private_id: ", end="", flush=False)
				private_id, user = self.new_user(private_id=private_id)
				if self.log:
					print(private_id)

			for i in images:
				if self.log:
					print("Saving face from: {}".format(i))
				user.save_face(i, log=self.log)

	#SAVE VIDEO WITH  FACES ON
	def video_write(self, video, folder="Saves"):
		video_capt = cv2.VideoCapture(video)

		frame_width = int(video_capt.get(3)) 
		frame_height = int(video_capt.get(4)) 

		size = (frame_width, frame_height) 

		frames = []

		video_save = cv2.VideoWriter("{}/".format(folder)+video.replace("/", ""), cv2.VideoWriter_fourcc(*'MP4V'), 20.0, size)
		while True:
			ret, frame = video_capt.read()

			if not ret:
				break
			else:
				frames.append(frame)

		finished_frames = []

		for f in frames:

			finished_frames.append(self.display_frame_faces(f, returnframe=True, wk=1, showvideo=False))

		for f in finished_frames:
			try:
				video_save.write(f)
			except:
				pass
	
	#SAVE ALL VIDEOS WITH FACES ON
	def videos_write_dir(self, folder="Videos", folder_save="Saves"):
		videos = glob.glob("{}/*.mp4".format(folder))

		for v in videos:
			self.video_write("{}".format(v), folder=folder_save)



	#WATCH ALL VIDEOS IN DIRECTORY
	def videos_watch_dir(self, folder="Videos"):
		videos = glob.glob("{}/*.mp4".format(folder))

		for v in videos:
			self.video("{}".format(v))

	#WATCH VIDEO
	def video_watch(self, video):
		video_capt = cv2.VideoCapture(video)

		while True:
			ret, frame = video_capt.read()

			#self.recogn_info_frame(frame)

			if not self.display_frame_faces(frame, True):
				break




	#SAVE ALL FRAMES FROM VIDEO TO A DIRECTORY
	def frames_save(self, video, dir="frames", n=0):
		video_capt = cv2.VideoCapture(video)

		i = 0

		while True:
			ret, frame = video_capt.read()

			if not ret:
				return ""

			try:
				cv2.imwrite("{}/{}{}.png".format(dir, n, i), cv2.normalize(frame, frame, 0, 255, cv2.NORM_MINMAX))
			except:
				pass
			print("{}/{}".format(i, "?"))

			i += 1

	#WATCH IMAGE
	def img_watch(self, image):
		frame = cv2.imread(image)
		return self.recogn_frame(frame)


	#CREATE NEW USER AND SAVE FACES
	def image_new_dir(self, folder):
		images = glob.glob(str(folder)+"/*.jpg")
		
		if len(images) > 0:

			private_id, new = self.new_user()

			if self.log:
				print("New user: {}" .format(private_id))

			self.record_faces(images, private_id=private_id)


	#LOOK IN DIRECTORY IF FACE IS UKNOWN NEW USER WILL BE CREATED AND IT WILL SAVE FACES
	def image_new_needed_dir(self, folder="*"):
		fold = self.images_folder + str(folder)
		print("Looking folder: {}".format(fold))
		images = glob.glob(fold+"/*.jpg")


		if len(images) > 0:

			private_id = self.no_one_on_sreen
			n = 0
			while private_id == self.no_one_on_sreen:
				try:
					i = images[n]
				except:
					break
				if self.log:
					print(i)
				private_id = self.re_img(i)
				n += 1

			if self.log:
				print(private_id)

			if not private_id:
				self.image_new_dir(fold)
			else:
				if self.log:
					print("Already know him ({})".format(private_id))
		else:
			if self.log:
				print("No images in {}".format(fold))

	def screen_new_needed(self, private_id=False):
		if not private_id:
			private_id, user = self.new_user()
		else:
			user = False
			for u in self.users:
				if u.private_id == private_id:
					user = u
					if self.log:
						print("User found")
					break
			if not user:
				if self.log:
					print("User not found, creating new user. Private_id: ", end="", flush=False)
				private_id, user = self.new_user(private_id=private_id)
				if self.log:
					print(private_id)

		sct = mss()

		mon = {'top': 300, 'left': 250, 'width': 1600, 'height': 870}

		while True:
			sct.get_pixels(mon)

			img = Image.frombytes('RGB', (sct.width, sct.height), sct.image)

			frame = arrayy(img)

			cv2.imshow("recording", frame)

			if self.log:
				print(private_id)

			user.record_frame(frame, log=self.log)

			if cv2.waitKey(1) & 0xFF == ord("q"):
				break


	def videos_new_needed(self, directory, private_id=False):
		videos = glob.glob(directory + "/*.mp4")

		if not private_id:
			private_id, user = self.new_user()
		for v in videos:
			self.video_new(v, private_id=private_id)

	def get_user(self, private_id=False):
		if not private_id:
			private_id, user = self.new_user()
		else:
			user = False
			for u in self.users:
				if u.private_id == private_id:
					user = u
					if self.log:
						print("User found")
					break
			if not user:
				if self.log:
					print("User not found, creating new user. Private_id: ", end="", flush=False)
				private_id, user = self.new_user(private_id=private_id)
				if self.log:
					print(private_id)

		return private_id, user


	#SAVE NEW USER AND FACES FROM VIDEO
	def video_new(self, video, private_id=False):
		trues = 0

		private_id, user = self.get_user(private_id)

		v = cv2.VideoCapture(video)
		while True:
			ret, frame = v.read()

			reframe = cv2.resize(frame, (self.resolution_width, self.resolution_height), interpolation=cv2.INTER_NEAREST)

			cv2.imshow("recording", reframe)

			if self.log:
				print(private_id)

			user.record_frame(frame, log=self.log)

			if cv2.waitKey(1) & 0xFF == ord("q"):
				break


	#SAVE NEW USER AND FACES FROM WEBCAM
	def webcam_new(self, private_id=False, min=20000):
		webcam = cv2.VideoCapture(0)
		trues = 0

		private_id, user = self.get_user(private_id)
		
		while True:
			ret, frame = webcam.read()

			cv2.imshow("recording", frame)

			private_id = False

			if self.log:
				print(private_id)

			if not private_id:
				user.record_frame(frame)
			else:
				if not private_id == self.no_one_on_sreen:
					trues += 1
					if self.log:
						print("Known face {}".format(trues))

			if trues > min:
				self.get_users()
				break

			if cv2.waitKey(1) & 0xFF == ord("q"):
				break



	def screen_watch(self, showvideo=False, showexample=False):
		while True:
			frame =  arrayy(ImageGrab.grab(bbox=(300,250, 1900, 1600)))

			if not self.display_frame_faces(frame, showvideo, showexample):
				break

	def reverse(self):
		webcam = cv2.VideoCapture(0)

		while True:
			ret, frame = webcam.read()

			#self.recogn_info_frame(frame)

			if not self.display_frame_faces(frame, True, False, reverse=True, track=False):
				break

	def webcam_watch(self, showvideo=True, showexample=False):
		webcam = cv2.VideoCapture(0)
 
		while True:
			ret, frame = webcam.read()

			#self.recogn_info_frame(frame)

			if not self.display_frame_faces(frame, showvideo, showexample):
				break


	#RECORD ALL NEW FACES FROM DIR WICH ONLY ACCEPTS DIRS THAT ARE NAMED  AS: Sollo ella or Solo yo
	def img_new_dir(self, main):
		people_dirs = scandir(main)

		durs = []

		for p in people_dirs:
			durs.append(p.name)

		if self.log:
			print("Starting record_news_from_dirs\n  -dirs: {}\n  -main: {}\n  -privates_ids_file: {}\n  -examples_folder: {}\n  -folder_recognition: {}\n\n".format(len(durs), main, self.privates_ids_file, self.examples_folder, self.folder_recognition))

		for person in durs:
			dirs = scandir(main + "/" + person)

			for d in dirs:
				d = d.name
				if d == "Solo el" or d == "Solo ella" or d == "Solo yo":
					dirr = main + "/" + person + "/" + d + "/"

					self.look_jpg_new_user(dirr)

			print("\n")

	def settings(self, pr=print):
		helps = [
		["privates_ids_file", self.privates_ids_file, False],
		["users", len(self.users), False],
		["images_folder", self.images_folder, False],
		["examples_folder", self.examples_folder, False],
		["folder_recognition", self.folder_recognition, False],
		["mode", self.mode, True],
		["load_names_delay", self.load_names_delay, False],
		["fail_to_destroy", self.fail_to_destroy, False],
		["minimun_decoded", self.minimun_decoded, True],
		["minim_porc", self.minim_porc, True],
		["log", self.log, True],
		["pedestrian_face_classifier", self.pedestrian_face_classifier, False],
		["autogetusers", self.autogetusers, True]
		]
		pr("Settings:")
		for n in helps:
			try:
				r = n[2]
				m = ""
				if r:
					m += "**"
			except:
				pass
			pr(" -" + self.printt(n[0], "{} {}".format( n[1], m)))

	def commands(self, key="", pr=print):
		f = " "
		s = "    "
		t = "      "
		q = ""

		functions = [
		["__init__", "Object type", [["mode", "Int", "Only 1 mode available: 0"], ["log", "Bool"], ["autogetusers", "Bool", "True to autoload users when calling the object"]]],
		["who", "Returns a array with objects about who is on the webcam", []],
		["img_new_dir", "Create users and save faces from images in a directory wich only reads from folders names: ['Solo ella', 'Solo yo']", [["dir", "String"]]],
		["webcam_watch", "Watch faces on webcam", [["showvideo", "Bool"], ["showexample", "Bool"]]],
		["screen_watch", "Watch faces on screen", [["showvideo", "Bool"], ["showexample", "Bool"]]],
		["img_watch", "Watch faces on img", [["image", "String", "Image name"]]],
		["videos_watch_dir", "Watch faces on videos from a directory", [["folder", "String"]]],
		["webcam_new", "Create new user and save faces from webcam", []],
		["video_new", "Create new user and save faces from video", [["video", "String", "Video name"]]],
		["videos_new_needed", "Create new users if needed and save faces from videos on directory", [["directory", "String"], ["private_id", "Integer", "Private id from the user"]]],
		["image_new_dir", "Create new user and save faces from images on directory", [["folder", "String"]]],
		["frames_save", "Save all frames from a video to a directory", [["video", "String", "Video name"], ["dir", "String", "Where frames will be saved"]]],
		["video_watch", "Watch faces on a video", [["video", "String", "Video name"]]],
		["videos_write_dir", "Save all videos from a directory with faces on", [["folder", "String", "Directory to grab the videos"], ["folder_save", "String", "Where the videos will be saved"]]],
		["video_write", "Save video with face on", [["video", "String", "Video name"], ["folder_save", "String", "Where the videos will be saved"]]],
		["image_new_needed_dir", "Create new user if doesnt exists and save faces from images on directory", [["folder", "String"]]],
		["images_new_needed_dir", "Create new users if doesnt exists and save faces from images on a directory", [["directory", "String"], ["private_id", "Integer", "Private id from the user"]]],
		["frame_faces_json", "Returns a json string with data about the face on the photo", [["frame", "NumpyArray", "Frame gotten from webcam, video or photo"]]]
		]

		pr("Functions:")
		for n in functions:
			if key in n[0] or key in n[1]:
				pr(f + "-" + n[0] + "")
				pr(s + "-Definition:\n{} ".format(t) + n[1] + " \n")
				printed_argument = False
				for a in n[2]:
					if not printed_argument:
						pr(s + "-Arguments:")

					printed_argument = True
					if len(a) > 2:
						inf = a[1] + ": " + a[2]
					else:
						inf = a[1]

					pr(t + "·" + self.printt(a[0], inf, decoration="-", le=30, mode=1))
				if not printed_argument:
					#pr("   -No arguments required")
					pass
				pr("")

	def search(self):
		self.commands(key=input("Search:"))

	def help(self, user_id, pr=print):
		self.settings(pr=pr)
		self.commands(pr=pr)

	def printt(self, first, second, le=200, decoration=".", mode=0):
		first = str(first)
		second = str(second)

		if mode == 0:
			n = le - (len(first) + len(second))
		else:
			if mode == 1:
				n = le - (len(first))

		r = ""
		if n > 0:
			for i in range(n):
				r += decoration
		return "{} {} {}".format(first, r, second)

	def who(self, min=5, camera=False):
		if not camera:
			camera = cv2.VideoCapture(0)

		people = []

		failed = 0

		for i in range(min):
			ret, frame = camera.read()

			if not ret:
				failed += 1
				if failed > 1:
					print("Camera disconnected")
					break
			else:
				failed = 0
				faces = self.pedestrian_face_tracker.detectMultiScale(frame)

				faces_frames = []

				for f in faces:
					fr = frame[f[1]:f[1]+f[3], f[0]:f[0]+f[2]]

					
					private_id = self.recogn_frame(fr)

					if private_id:
						if not private_id == self.no_one_on_sreen: 
							exists = False
							for p in people:
								if p[1] == private_id:
									exists = True
									p[2] += 1

							if not exists:
								people.append([fr, private_id, 1])

		return people









	def webcam_watch_faces_boxes(self):
		boxes =  ""

	def __init__(self, mode=0, log=False, autogetusers=True, minimun_decoded=1, minim_porc=70):
		self.privates_ids_file = "data.json"
		self.users = []
		self.images_folder = ""
		self.examples_folder = "Examples/"
		self.folder_recognition = "Encodes/"

		self.mode = mode
		self.load_names_delay = 20
		self.fail_to_destroy = 0
		self.minimun_decoded = minimun_decoded
		self.log = log

		self.no_one_on_sreen = "NOOOOOOOO"

		self.pedestrian_face_classifier = 'haarcascade_frontalface_default.xml'
		self.pedestrian_face_tracker = cv2.CascadeClassifier(cv2.data.haarcascades + self.pedestrian_face_classifier)

		self.autogetusers = autogetusers

		self.resolution_width = 480
		self.resolution_height = 520


		self.display_frame_faces_oldfaces = []

		self.minim_porc = minim_porc
		self.proc_minim = True

		if autogetusers:
			self.get_users()


if __name__ == "__main__":
	argv = sys.argv[1:]

	log = True
	for a in argv:
		if a[0] == "l":
			log = True

	re = rec(log=log, minimun_decoded=10, autogetusers=True)

	for p in argv:
		if p[0] == "h":
			re.help()

	re.webcam_watch()