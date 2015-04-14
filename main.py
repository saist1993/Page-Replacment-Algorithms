#DOUBT - Can instruction count be called as our unit time?


import os

#We need to read from a file and save the parsed meta data in an list .
#Let all the temporary variable begin with "_" that is underscore 
input = []
virtualMemory = []
ram=[]
class Page:
	def __init__(self, index, size, frame_index,process, startLocation):
		self.size = size
		self.process = process
		self.frame_index = frame_index
		self.index = index
		self.location=startLocation

	def isMapped(self):
		if self.frame_index != -1:
			return True
		return False

	def printable(self):
		return 'Process: %(process)s, frame_index: %(frame_index)s, index: %(index)s, location = %(location)s' % {'process': self.process, 'frame_index': self.frame_index, 'index': self.index, 'location': self.location}

class Frame:											#Ram
	def __init__(self, index, size, startLocation):
		self.size=size
		self.location=startLocation
		self.index=index
		self.instruction_count = -1			#Only to be used for LRU
		self.time_fetched = 0
		self.permissions_read = False
		self.permissions_write = False
		self.ismapped = False

	def isReferenced(self,instruction_count):		#Only to be used for LRU
		self.instruction_count = instruction_count

	def isFetched(self,instruction_count):			#Only to be used for FIFO
		self.time_fetched = instruction_count

	def printable(self):
		return 'ismapped: %(ismapped)s, index: %(index)s, location = %(location)s' % {'ismapped': self.ismapped, 'index': self.index, 'location': self.location}

#Variables that might affect the simulation		
page_size = 128
frame_size = 4
number_of_pages = 4000	#Size of virtual memory
number_of_frames = 2000 #Size of main memory
size = 128

#only for LRU (or unit time)
instruction_count = 0


traces_dir = os.path.join(os.path.dirname(__file__),'traces')

def findPage(location):
	#Finds a page based on an address.
	#The page retured belongs to virtual memory.
	global instruction_count
	print "len" + str(len(virtualMemory))
	for index in range(len(virtualMemory)):
		lowerIndex = virtualMemory[index].location
		try:
			upperIndex = virtualMemory[index+1].location
		except:
			return	
		if int(location) >= int(lowerIndex) and int(location) < int(upperIndex):
			return virtualMemory[index]

def LRU():
	for node in input:
		location = int(str(node[2]),16)	#converting it into integer
		page = findPage(location)
		if page:
			print "found page"
		else:
			print "no page found"

def least_recently_used(self):
	global ram
	
	#Find first mapped page and put it in candidate var
	candidate = None
	for frame in ram:
		if frame.ismapped:
			candidate = frame
			break
		else:
			return frame

	#By now either we did find an empty frame and threw it out to be replaced or we have a value in candidate

	for frame in ram:
		if frame.ismapped and frame.instruction_count < candidate.instruction_count :
			candidate = frame
		else:
			return frame

	return candidate
			
def first_in_first_out(self):
	global ram

	#Put first mapped page into candidate var
	candidate = None
	for frame in ram:
		if page.ismapped:
			candidate = frame
		else:
			return frame

	#By now either we did find an empty frame and threw it out to be replaced or we have a value in candidate	

	for frame in ram:
		if frame.ismapped and frame.time_fetched < candidate.time_fetched :
			candidate = frame

	return candidate

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

def simulate():
	global virtualMemory, ram, instruction_count, input
	#for line in input:
		#print line #Can render the trace file perfectly
	for frame in ram:
		print frame.printable()

if __name__ == "__main__":
	readFile(os.path.join(traces_dir,'example_trace.txt'))
	_startlocation = 0
	for index in range(number_of_pages):
		page = Page(index, page_size, -1, -1, _startlocation)
		virtualMemory.append(page)
		_startlocation=_startlocation + page_size

	location = 0
	for index in range(number_of_frames):
		frame = Frame(index,frame_size,location)
		location = location + size
		ram.append(frame)

	#The virtual memory and RAM have been setup by now
	simulate()
# a simple function which either returns null or relevent Page object.





#lets code least recenty used algorithm 
