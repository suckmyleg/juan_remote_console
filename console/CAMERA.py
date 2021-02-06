
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