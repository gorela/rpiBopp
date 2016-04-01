import time
import os
class glo(object):
	"""docstring for glo"""
	text = "ji was ist denn das alles fuer nen dreck... sind das schon genug?"
	text2 = text + "    " + text
	dw = 30;
	def __init__(self, arg):
		super(glo, self).__init__()
		self.text = arg
		
lo = glo("alter")		
print(glo.text)
print(lo.text)

for i in range(1000):
	time.sleep(0.2)
	os.system("clear")
	print(glo.text2[i%(len(glo.text)+1):((i%len(glo.text)+glo.dw))])
	#print(glo.text[5:-1])