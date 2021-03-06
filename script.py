import os
import random

#Variables that might affect the simulation		
page_size = 128
frame_size = 128
number_of_pages = 500	#Size of virtual memory
number_of_frames = 250	#Size of main memory
second_chance_cycle_time = 10
#only for LRU (or unit time)
instruction_count = 0
fault_count = 0
hit_count = 0

#For adaptive average algos
adaptive_average_size = number_of_pages/50
adaptive_average_tolerance_ratio = 3.0
pre_emptive_adaptive_index = 0
pre_emptive_adaptive_size = 50

traces_dir = os.path.join(os.path.dirname(__file__),'traces')

virtualMemory = None
ram = None
#In use for the IBM Algorithm
frequency = None
recency = None
frequency_ghost = None
recency_ghost = None
p = 2*number_of_pages/3
ghost_size += number_of_pages/2

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
		self.occurance = 0

	def isReferenced_read(self,instruction_count):		#Only to be used for LRU
		self.last_referred = instruction_count

	def isFetched(self,instruction_count):			#Only to be used for FIFO
		self.time_fetched = instruction_count

	def isReferenced_write(self,instruction_count):
		self.last_wrote = instruction_count

	def isOccured(self):
		self.occurance += 1
	
	def lastAccessed(self):
		return self.last_referred

	def isMapped(self):
		if self.frame_index > -1:
			return True
		return False

	def printable(self):
		return 'Process: %(process)s, frame_index: %(frame_index)s, index: %(index)s, location = %(location)s time_fetched = %(time)d' % {'process': self.process, 'frame_index': self.frame_index, 'index': self.index, 'location': self.location, 'time': self.time_fetched}
class Frame:											#Ram
	def __init__(self, index, size, startLocation):
		self.size=size
		self.location=startLocation
		self.index=index
		self.ismapped = False
		self.page_index = -1

	def printable(self):
		return 'ismapped: %(ismapped)s, index: %(index)s, location = %(location)s' % {'ismapped': self.ismapped, 'index': self.index, 'location': self.location}
class Ram:
	def __init__(self,ram,frame_size):
		self.ram = ram
		self.first_unmapped = 0
		self.length = len(ram)
		self.frame_size = frame_size
	def printable(self):
		printout = ''
		for frame in self.ram:
			printout += frame.printable()
			printout += '\n'
		return printout
	#def replacing(self,frame_index);
			
	def replacing(self,frame_index):
		if self.first_unmapped == frame_index:	#fifo returns the frame index.. thats is replace this frame
			for frame in self.ram:
				if frame.index > self.first_unmapped:
					if not frame.ismapped:
						self.first_unmapped = frame.index
						return
			else:
				self.first_unmapped = -1
	def get(self,frame_index):
		if frame_index <= len(self.ram):
			return self.ram[frame_index]
class VirtualMemory:
	def __init__(self,virtualMemory):
		self.virtualMemory = virtualMemory
		self.size = len(virtualMemory)
	def printable(self):
		printout = ''
		for page in self.virtualMemory:
			printout += page.printable()
			printout += '\n'
		return printout
	def get(self,page_index):
		if page_index <= len(self.virtualMemory):
			return self.virtualMemory[page_index]
class ibm:
	def __init__(page):
		self.recency, self.frequency = init_ibm()

	def inGhost(self,page):
		if 

def init_ram():
	location = 0
	ram = []
	for index in range(number_of_frames):
		frame = Frame(index,frame_size,location)
		location = location + frame_size
		ram.append(frame)
	return ram
def init_virtualMemory():
	virtualMemory = []
	_startlocation = 0
	for index in range(number_of_pages):
		page = Page(index, page_size, -1, -1, _startlocation)
		virtualMemory.append(page)
		_startlocation=_startlocation + page_size
	return virtualMemory
def init_ibm():
	global virtualMemory,recency,p
	for i in range(p):
		recency.append(virtualMemory.get(i))
	for i in range(p,virtualMemory.size):
		frequency.append(virtualMemory.get(i))
	return recency, frequency		

def findPage(location):
	#Finds a page based on an address.
	#The page retured belongs to virtual memory.
	global instruction_count
	#print "len" + str(len(virtualMemory))
	for index in range(virtualMemory.size):
		lowerIndex = virtualMemory.get(index).location
		try:
			upperIndex = virtualMemory.get(index+1).location
		except:
			return	
		if int(location) >= int(lowerIndex) and int(location) < int(upperIndex):
			return virtualMemory.get(index)
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

#ALGOS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def first_in_first_out():
	global virtualMemory,ram

	if ram.first_unmapped >= 0:
		return ram.first_unmapped
	#Put first mapped page into candidate var
	#Find first mapped page and put it in candidate var
	candidate = None
	for i in range(virtualMemory.size):
		page = virtualMemory.get(i)
		if page.isMapped():
			candidate = page
			break

	for j in range(i,virtualMemory.size):
		page = virtualMemory.get(j)
		if page.isMapped() and page.time_fetched <= candidate.time_fetched :
			candidate = page

	return candidate.frame_index
def second_chance_first_in_first_out():
	global virtualMemory,ram,second_chance_cycle_time

	if ram.first_unmapped >= 0:
		return ram.first_unmapped
	while True:
		candidate = None
		for i in range(virtualMemory.size):
			page = virtualMemory.get(i)
			if page.isMapped():
				candidate = page
				break

		for j in range(i,virtualMemory.size):
			page = virtualMemory.get(j)
			if page.isMapped() and page.time_fetched <= candidate.time_fetched :
				candidate = page

		if not candidate.lastAccessed() - candidate.time_fetched >= 1:
			print "SAVED"
			return candidate.frame_index
		else:
			candidate.time_fetched = instruction_count
			candidate.last_referred = instruction_count
def least_recently_used():
	global virtualMemory,ram
	if ram.first_unmapped >= 0:
		return ram.first_unmapped

	#Find first mapped page and put it in candidate var
	candidate = None
	for i in range(virtualMemory.size):
		page = virtualMemory.get(i)
		if page.isMapped():
			candidate = page
			break

	for j in range(i,virtualMemory.size):
		page = virtualMemory.get(j)
		if page.isMapped() and page.last_referred <= candidate.last_referred:
			candidate = page

	return candidate.frame_index
def preemptive_adaptive_least_recently_used():
	global virtualMemory,ram,pre_emptive_adaptive_index,pre_emptive_adaptive_size

	if ram.first_unmapped >= 0:
		return ram.first_unmapped
	#Put first mapped page into candidate var
	#Find first mapped page and put it in candidate var
	candidate = None
	while True:
		for i in range(pre_emptive_adaptive_index, min(virtualMemory.size,pre_emptive_adaptive_index + pre_emptive_adaptive_size)):
			page = virtualMemory.get(i)
			if page.isMapped():
				candidate = page
				break	

		if not candidate is None:
			break
		else:
			if pre_emptive_adaptive_index + pre_emptive_adaptive_size < virtualMemory.size:
				pre_emptive_adaptive_index += pre_emptive_adaptive_size
			else:
				#Overflow could have or must have happened
				pre_emptive_adaptive_index = 0
	#now candidate surely is not none
	for i in range(pre_emptive_adaptive_index,min(pre_emptive_adaptive_index+pre_emptive_adaptive_size,virtualMemory.size)):
		page = virtualMemory.get(i)
		if page.isMapped() and page.last_referred <= candidate.last_referred:
			candidate = page

	return candidate.frame_index
def average_adaptive_least_recently_used():
	global virtualMemory,ram,pre_emptive_adaptive_index,pre_emptive_adaptive_size

	if ram.first_unmapped >= 0:
		return ram.first_unmapped

	#now candidate surely is not none and only one item has been scanned in this area
	sum = 0
	mapped = 0
	for i in range(pre_emptive_adaptive_index,virtualMemory.size):
		page = virtualMemory.get(i)
		if page.isMapped():
			mapped += 1
			sum += instruction_count - page.last_referred
			if mapped > adaptive_average_size:
				if instruction_count - page.last_referred <= (float(sum)/mapped)/adaptive_average_tolerance_ratio:
					#Then simply return this shit.
					pre_emptive_adaptive_index = i
					return page.frame_index

	#If the control comes here, then we did not find any suitable thing.
	candidate = virtualMemory.get(random.randint(pre_emptive_adaptive_index,virtualMemory.size))
	pre_emptive_adaptive_index = 0
	return candidate.frame_index
def least_frequently_used():
	global virtualMemory,ram

	if ram.first_unmapped >= 0:
		return ram.first_unmapped
	#Put first mapped page into candidate var
	#Find first mapped page and put it in candidate var
	candidate = None
	for i in range(virtualMemory.size):
		page = virtualMemory.get(i)
		if page.isMapped():
			candidate = page
			break

	for j in range(i,virtualMemory.size):
		page = virtualMemory.get(j)
		if page.isMapped() and page.occurance <= candidate.occurance :
			candidate = page

	return candidate.frame_index
def ibm():

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
#HIT COUNTERS~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def hit_least_frequently_used(page):
	page.isOccured()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def page_fault():
	global instruction_count,ram
	#Currently running FIFO
	frame_index = average_adaptive_least_recently_used()
	ram.replacing(frame_index)
	return frame_index
def environment():
	global virtualMemory, ram, instruction_count, input, fault_count

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
			#print line, "Permissions not recognized"
			continue
		if not page:
			#Huh! This should not have happened. Let us ignore?
			#print line, "Memory Location Out of Bounds"
			continue
		try:
			process = int(line[0].strip())
		except:
			#print line, "Process ID is not an ID :/"
			continue	


		#print line
		#print "page referenced: ", page.printable()
		#Good to go with the three variables.
		#Let's see if the page is mapped or not

		page.isOccured()
		if page.isMapped() and page.process == process:
			#Cool. Better go and just update the time
			
			if not page.frequency:
				page.frequency = True
			
			page.isReferenced_read(instruction_count)
			if permissions:
				page.isReferenced_write(instruction_count)

		#HIT ENDS
		else:
			#Page fault just happened.
			frame_index = page_fault()
			#print "D`EBUG", frame_index
			page.permissions_read = True
			page.last_referred = -1
			page.last_wrote = -1
			if permissions:
				page.permissions_write = True
			#Specified that the frame has been mapped to a page and its permissions have been mentioned.

			#ACTUAL MAPPING#
			page.frame_index = frame_index 						#Actual mapping of the frame to new page
			old_page = virtualMemory.get(ram.get(frame_index).page_index)
			old_page.frame_index = -1

			ram.get(frame_index).page_index = page.index
			page.process = process 					#What process is running in the page
			ram.get(frame_index).ismapped = True
			#print "DEBUG!!!!!!!!"
			page.time_fetched = instruction_count

			#This frame will be returned with its variables appropriately set. 
			#Need to update it's time counters now.
			page.isReferenced_read(instruction_count)
			if permissions:
				#i.e. if the page's permissions were write as well
				page.isReferenced_write(instruction_count)
			fault_count += 1
			#print "frame replaced: ", page.printable()
		#print "\n"
		instruction_count += 1

if __name__ == "__main__":
	readFile(os.path.join(traces_dir,'vm_trace_fragment_two.txt'))
	ram = Ram(init_ram(),frame_size)
	virtualMemory = VirtualMemory(init_virtualMemory())
	environment()
	print "faults: ", fault_count
	print "instructions: ", instruction_count
	'''for page in virtualMemory.virtualMemory:
					print page.index, page.occurance'''