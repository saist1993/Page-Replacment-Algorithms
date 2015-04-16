#DOUBT - Can instruction count be called as our unit time?


import os

#We need to read from a file and save the parsed meta data in an list .
#Let all the temporary variable begin with "_" that is underscore 
input = []
class Page:
	def __init__(self, index, size, frame_index,process, startLocation):
		self.size = size
		self.process = process
		self.frame_index = frame_index
		self.index = index
		self.location=startLocation		
		self.last_referred = -1			#Only to be used for LRU
		self.last_wrote = -1
		self.time_fetched = 0
		self.permissions_read = False
		self.permissions_write = False

	def isReferenced_read(self,instruction_count):		#Only to be used for LRU
		self.last_referred = instruction_count

	def isFetched(self,instruction_count):			#Only to be used for FIFO
		self.time_fetched = instruction_count

	def isReferenced_write(self,instruction_count):
		self.last_wrote = instruction_count

	def lastAccessed(self):
		if not self.ismapped:
			return -1
		if self.last_wrote == -1:
			return self.last_referred
		if self.last_wrote > self.last_referred:
			return self.last_wrote
		else:
			return self.last_referred

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
		self.ismapped = False

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

virtualMemory = []
ram = []

def findPage(location):
	#Finds a page based on an address.
	#The page retured belongs to virtual memory.
	global instruction_count
	#print "len" + str(len(virtualMemory))
	for index in range(len(virtualMemory)):
		lowerIndex = virtualMemory[index].location
		try:
			upperIndex = virtualMemory[index+1].location
		except:
			return	
		if int(location) >= int(lowerIndex) and int(location) < int(upperIndex):
			return virtualMemory[index]

##################################################ALGORITHMS######################################################################

def least_recently_used():
	global virtualMemory
	
	#Find first mapped page and put it in candidate var
	candidate = None
	for page in virtualMemory:
		if page.isMapped():
			candidate = page
			break
		else:
			return page

	#By now either we did find an empty frame and threw it out to be replaced or we have a value in candidate

	for page in virtualMemory:
		if page.ismapped and page.lastAccessed() < candidate.lastAccessed() :
			candidate = page
		else:
			return page

	return candidate
			
def first_in_first_out():
	global virtualMemory

	#Put first mapped page into candidate var
	candidate = None
	for frame in virtualMemory:
		if page.ismapped:
			candidate = page

	#By now either we did find an empty frame and threw it out to be replaced or we have a value in candidate	

	for page in virtualMemory:
		if page.ismapped and page.time_fetched < candidate.time_fetched :
			candidate = page

	return candidate

##################################################ENVIRONMENT#####################################################################

#This function is expected to find a relevant frame, and map it with our page and make the system ready to proceed
def page_fault(process,permissions,page):
	global instruction_count

	#Currently running FIFO
	page = first_in_first_out()
	return page


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

def environment():
	global virtualMemory, ram, instruction_count, input

	for line in input:	
		#print line
		page = None					#Object of page which is in the location
		permissions = None			#True if write, else false
		process = None

		page = findPage(int(str(line[2]),16))
		if str(line[1]).upper() == 'R':
			permissions = True
		elif str(line[1]).upper() == 'W':
			permissions = False
		else:
			#Weird set of permissions
			print line, "Permissions not recognized"
			continue
		if not page:
			#Huh! This should not have happened. Let us ignore?
			print line, "Memory Location Out of Bounds"
			continue
		try:
			process = int(line[0])
		except:
			print line, "Process ID is not an ID :/"
			continue
		if not process.__class__ == int('3').__class__:
			print line, "Process ID is not an ID :/"
			continue

		print line
		print "page referenced: ", page.printable()
		#Good to go with the three variables.
		#Let's see if the page is mapped or not
		if page.isMapped() and page.process == process:
			#Cool. Better go and just update the time
			frame = ram[page.frame_index]
			if frame.__class__ != ram[0].__class__:
				#Something went wrong. The page was mapped to a non existant frame
				continue
			page.isReferenced_read(instruction_count)
			if permissions:
				page.isReferenced_write(instruction_count)
			print "frame found: ", page.printable()

		#HIT ENDS
		else:
			#Page fault just happened.
			page = page_fault(process,permissions,page)
			page.permissions_read = True
			if permissions:
				page.permissions_write = True
			#Specified that the frame has been mapped to a page and its permissions have been mentioned.

			page.frame_index = frame.index 			#Actual mapping
			page.process = process 					#What process is running in the page
			page.time_fetched = instruction_count
			#This frame will be returned with its variables appropriately set. 
			#Need to update it's time counters now.
			page.isReferenced_read(instruction_count)
			if permissions:
				#i.e. if the page's permissions were write as well
				page.isReferenced_write(instruction_count)

			print "frame replaced: ", page.printable()
			
			#now the frame has been mapped as well as its values updated. Can continue now 

		instruction_count += 1
		#Let us go and update the referenced 


def init_ram():
	location = 0
	ram = []
	for index in range(number_of_frames):
		frame = Frame(index,frame_size,location)
		location = location + size
		ram.append(frame)
	return ram

def init_virtualMemory():
	virtualMemory = []
	for index in range(number_of_pages):
		page = Page(index, page_size, -1, -1, _startlocation)
		virtualMemory.append(page)
		_startlocation=_startlocation + page_size
	return virtualMemory

if __name__ == "__main__":
	readFile(os.path.join(traces_dir,'example_trace.txt'))
	_startlocation = 0
	



	#The virtual memory and RAM have been setup by now
	environment()
# a simple function which either returns null or relevent Page object.





#lets code least recenty used algorithm 
