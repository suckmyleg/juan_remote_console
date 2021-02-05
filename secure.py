import os
from pylab import *
import rec as recc
import numpy as np

def off():
	#os.system("xset dpms force off")
	print("Off")
def on():
	#os.system("xset dpms force on") 
	print("On")
def sc(onn, failed):
	if onn:
		on()
		failed = 0
	else:
		failed += 1
		if failed > 15:
			off()
	return failed

def graph_people(people, times):
	for p in people:
		p[2].append(p[1])
		plot(np.arange(times), p[2] + p[2], label=str(p[0]))
	show()
	return people
re = recc.rec()

onn = False

times = 1

failed = -1

faces_record = []

for i in range(1000):
	failed = sc(onn, failed)
	faces = re.who(min=5)
	onn = False
	for f in faces:
		exists = False
		for r in faces_record:
			#print(f, r[0])
			if f[1] == r[0]:
				exists = True
				r[1] += 1
		if not exists:
			faces_record.append([f[1], 0, []])		
		names = re.get_names(f[1])
		print(names)
		if "SukMyLeg" == names[0]:
			onn = True
			sc(onn, failed)
	faces_record = graph_people(faces_record, times)
	failed = sc(onn, failed)
	times += 1

on()