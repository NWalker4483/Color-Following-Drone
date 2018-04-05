import os
colors={
"default" : "\033[0m",
"red" : "\033[91m",
"green" : "\033[92m",
"yellow" : "\033[93m",
"blue" : "\033[94m",
"purple" : 	"\033[95m",
"linneup" : "\033[1A"}
def writeout(*args,color='default'):
	if os.name == 'posix':
		print(colors[color]),
	try:
		if len(*args) > 0:
			for i in args:	print (i),
			print(colors['default'])
	except: pass
writeout("Potato",color='blue')