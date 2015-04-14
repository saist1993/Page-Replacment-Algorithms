import os

#We need to read from a file and save the parsed meta data in an list .
#Let all the temporary variable begin with "_" that is underscore 
input = []
virtualMemory = []
ram=[]

page_size = 4
frame_size = 4
number_of_pages = 4000	#Size of virtual memory
number_of_frames = 2000 #Size of main memory


def readFile(path):	#it takes path with file name as input
	global input
	_counter=0				#temporary counter
	_list = []				#temporary list for clearing out excess inputs like space and new line
	if os.path.isfile(path):#check if file exists  
		with open(path,"r") as fo:
			for line in fo:
				_list=line[:].split(",")
				
				#clearing white space and \r\n
				for node in range(len(_list)):
					_list[node]=_list[node].strip()					#strips white spaces	
					_list[node]=_list[node].strip('\r\n')			#strips "\r\n"
							
				input.append(_list)
	else:
		print "path does not exists"	


#Now a class for the read. The reason for class is that we can add various parametrs later on 
#This class has following functions for now 
# Read, Name of the Process , Memory Location''' 
class Page:
	def __init__(self, index, size, frame_index,process):
		self.size = size
		self.process = process
		self.content = frame_index
		self.index = index

class Frame:
	def __init__(self, index, size, startLocation):
		self.size=size
		self.Location=startLocation
		self.index=index

if __name__ == "__main__"
	readFile("/home/gaurav/OperatingSystem/Project/example_trace.txt")
	for index in range(number_of_pages):
		page = Page(index, page_size, -1, -1)
		virtualMemory.append(page)

	location = 0
	for index in range(number_of_frames):
		frame = Frame(index,frame_size,location)
		location = location + size
		ram.append(frame)

	#The virtual memory and RAM have been setup by now
