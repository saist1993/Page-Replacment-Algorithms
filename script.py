import os
import random
import packet
import matplotlib.pyplot as plt
plt.ylabel('Page Fault Ratio')
plt.xlabel('Number of Pages')

#Variables that might affect the simulation		
page_size = 256
frame_size = 256
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

is_using_ibm = False
ibm = None

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
	def find_next_free(self):
		for frame in self.ram:
			if not frame.ismapped:
				return frame.index
		return -1		
	def set_next_free(self):
		for frame in self.ram:
			if not frame.ismapped:
				self.first_unmapped = frame.index
				return
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
class IBM:
	def __init__(self):
		self.frequency = []
		self.recency = []
		self.recency_ghost = []
		self.frequency_ghost = []
		self.recency_size = number_of_pages/2
		self.frequency_size = number_of_pages/2
		self.ghost_size = number_of_pages/2

	def add_to_frequency(self,page):
		if len(self.frequency) < self.frequency_size:
			frame_index = ram.find_next_free()
			if frame_index == -1:
				#Something is wrong
				print "Error, expected free frame. Not found"
			else:
				page.frame_index = frame_index
				ram.get(frame_index).ismapped = True
				ram.set_next_free()
				self.frequency.append(page)
		else:
			old_page = self.frequency.pop(0)
			frame_index = old_page.frame_index
			if frame_index == -1:
				print "Errror, expected the frame index to be existant. Not so"
			old_page.frame_index = -1
			page.frame_index = frame_index
			self.add_to_ghost_frequency(old_page)
			self.frequency.append(page)

	def add_to_recency(self,page):
		if len(self.recency) < self.recency_size:
			frame_index = ram.find_next_free()
			if frame_index == -1:
				#Something is wrong
				#print len(self.recency), self.recency_size
				print "Error, expected free frame. Not found!"
			else:
				page.frame_index = frame_index
				ram.get(frame_index).ismapped = True
				ram.set_next_free()
				self.recency.append(page)
		else:
			old_page = self.recency.pop(0)
			frame_index = old_page.frame_index
			if frame_index == -1:
				print "Errror, expected the frame index to be existant. Not so!"
			old_page.frame_index = -1
			page.frame_index = frame_index
			self.add_to_ghost_recency(old_page)
			self.recency.append(page)

	def add_to_ghost_frequency(self,page):
		if not page.frame_index == -1:
			print "Error, Expected the page to be unmapped"
			ram.get(page).ismapped = False
			ram.set_next_free()
			page.frame_index = -1
		if len(self.frequency_ghost) <= self.ghost_size:
			self.frequency_ghost.append(page)
		else:
			self.frequency_ghost.pop(0)
			self.frequency_ghost.append(page)

	def add_to_ghost_recency(self,page):
		if not page.frame_index == -1:
			print "Error, Expected the page to be unmapped"
			ram.get(page.frame_index).ismapped = False
			ram.set_next_free()
			page.frame_index = -1
		if len(self.recency_ghost) <= self.ghost_size:
			self.recency_ghost.append(page)
		else:
			self.recency_ghost.pop(0)
			self.recency_ghost.append(page)

	def found_in_ghost_frequency(self,page):
		if len(self.frequency) == number_of_frames:	#Might throw some issue
			self.frequency_ghost.remove(page)
			self.add_to_frequency(page)
		else:
			self.frequency_size += 1
			if len(self.recency) < self.recency_size:
				self.recency_size -= 1
			else:
				old_page = self.recency.pop(0)
				old_page.frame_index = -1
				ram.get(page.frame_index).ismapped = False
				ram.set_next_free()
				self.recency_size -= 1
				self.add_to_ghost_frequency(old_page)
			self.add_to_frequency(page)

	def found_in_ghost_recency(self,page):
		if len(self.recency) == number_of_frames:	#Might throw some issue
			self.recency_ghost.remove(page)
			self.add_to_recency(page)
		else:
			self.recency_size += 1
			if len(self.frequency) < self.frequency_size:
				self.frequency_size -= 1
			else:
				old_page = self.frequency.pop(0)
				old_page.frame_index = -1
				ram.get(page.frame_index).ismapped = False
				ram.set_next_free
				self.frequency_size -= 1
				self.add_to_ghost_recency(old_page)
			self.add_to_recency(page)

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
	fo.close()

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
			#print "SAVED"
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
def least_recently_used_minus_k(k = 2):
	global virtualMemory,ram,instruction_count
	if ram.first_unmapped >= 0:
		return ram.first_unmapped

	tries = 0
	while tries <= k:
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
		candidate.last_referred = instruction_count
		tries += 1

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
	if candidate == None:
		print "WHATTTTTTTTTTTTTTTT"

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
	candidate = virtualMemory.get(random.randint(pre_emptive_adaptive_index,virtualMemory.size-1))
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
#HIT COUNTERS~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def hit_least_frequently_used(page):
	page.isOccured()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def page_fault(choice = 'ibm',var = 2):
	global instruction_count,ram
	#Currently running FIFO
	if choice == 'first_in_first_out':
		frame_index = first_in_first_out()
	if choice == 'second_chance_first_in_first_out':
		frame_index = second_chance_first_in_first_out()
	if choice == 'least_recently_used':
		frame_index = least_frequently_used()
	if choice == 'least_recently_used_minus_k':
		frame_index = least_recently_used_minus_k(var)
	if choice == 'preemptive_adaptive_least_recently_used':
		frame_index = preemptive_adaptive_least_recently_used()
	if choice == 'average_adaptive_least_recently_used':
		frame_index = average_adaptive_least_recently_used()
	if choice == 'least_frequently_used':
		frame_index = least_frequently_used()

	ram.set_next_free()
	return frame_index
def environment(choice,var):
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

		#print line
		#print "page referenced: ", page.printable()
		#Good to go with the three variables.
		#Let's see if the page is mapped or not

		page.isOccured()
		if is_using_ibm:
			instruction_count += 1
		#print instruction_count
		if page.isMapped():
			#Cool. Better go and just update the time
			
			if is_using_ibm:
				#print "HIT"
				found = False
				for _page in ibm.frequency:
					if _page.index == page.index:
						ibm.frequency.remove(_page)
						ibm.frequency.append(_page)
						found = True
						break
				if not found:
					for _page in ibm.recency:
						if _page.index == page.index:
							ibm.recency.remove(_page)
							frame_index = _page.frame_index
							_page.frame_index = -1
							ram.get(frame_index).ismapped = False
							ram.set_next_free()
							ibm.add_to_frequency(_page)
							found = True
							break
				if not found:
					#Something fishy
					print "Error, was supposed to find a match in either frequency or recency. Not so"
				continue
			#print "HERE"
			page.isReferenced_read(instruction_count)
			if permissions:
				page.isReferenced_write(instruction_count)

		#HIT ENDS
		else:		
			fault_count += 1
			if is_using_ibm:
				found = False
				for _page in ibm.frequency_ghost:
					if _page.index == page.index:
						ibm.found_in_ghost_frequency(page)
						found = True
						break
				if not found:
					for _page in ibm.recency_ghost:
						if _page.index == page.index:
							ibm.found_in_ghost_recency(page)
							found = True
							break
				if not found:
					print instruction_count, ram.find_next_free(), len(ibm.frequency), len(ibm.recency)
					ibm.add_to_recency(page)
				continue

			#print "HERE"

			#Page fault just happened.
			frame_index = page_fault(choice,var)

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
			ram.get(frame_index).ismapped = True
			ram.set_next_free()
			#print "DEBUG!!!!!!!!"
			page.time_fetched = instruction_count

			#This frame will be returned with its variables appropriately set. 
			#Need to update it's time counters now.
			page.isReferenced_read(instruction_count)
			if permissions:
				#i.e. if the page's permissions were write as well
				page.isReferenced_write(instruction_count)

			#print "frame replaced: ", page.printable()
		#print "\n"
		if not is_using_ibm:
			instruction_count += 1

	return instruction_count,fault_count


output_pages = []
first_in_first_out_output_fault_ratios = []
least_recently_used_output_fault_ratios = []
second_chance_first_in_first_out_output_fault_ratios = []
least_recently_used_minus_k_output_fault_ratios = []
preemptive_adaptive_least_recently_used_output_fault_ratios = []
average_adaptive_least_recently_used_output_fault_ratios = []
least_frequently_used_output_fault_ratios = []
ibm_output_fault_ratios = []

def output_fault_ratios(ratio,type):
	if type == 'first_in_first_out':
		first_in_first_out_output_fault_ratios.append(ratio)
	if type == 'least_recently_used':
		least_recently_used_output_fault_ratios.append(ratio)
	if type == 'second_chance_first_in_first_out':
		second_chance_first_in_first_out_output_fault_ratios.append(ratio)
	if type == 'least_recently_used_minus_k':
		least_recently_used_minus_k_output_fault_ratios.append(ratio)
	if type == 'preemptive_adaptive_least_recently_used':
		preemptive_adaptive_least_recently_used_output_fault_ratios.append(ratio)
	if type == 'average_adaptive_least_recently_used':
		average_adaptive_least_recently_used_output_fault_ratios.append(ratio)
	if type == 'least_frequently_used':
		least_frequently_used_output_fault_ratios.append(ratio)
	if type == 'ibm':
		ibm_output_fault_ratios.append(ratio)

for type in ['first_in_first_out','second_chance_first_in_first_out','least_recently_used','least_recently_used_minus_k','preemptive_adaptive_least_recently_used','average_adaptive_least_recently_used','least_frequently_used','ibm']:
	print type
	for num in range(500,10000,500):
		instruction_count = 0
		fault_count = 0
		number_of_frames = num/2
		number_of_pages = num
		ram = Ram(init_ram(),frame_size)
		virtualMemory = VirtualMemory(init_virtualMemory())
		ibm = IBM()
		input = []
		readFile(os.path.join(traces_dir,'vm_trace_fragment_two.txt'))
		choice,var = type,2
		if choice == 'ibm':
			is_using_ibm = True

		instructions,faults = environment(choice,var)

		output_fault_ratios(float(fault_count)/float(instruction_count),type)
		#print "number of pages: ", num
		#print "faults: ", faults
		#print "instructions: ", instructions
		#print "length of ram", ram.length
		#print "length of vm", virtualMemory.size
		#print "RATIO: ", float(fault_count)/float(instruction_count)
		#print "\n"

for num in range(500,10000,500):
	output_pages.append(num)
#Plotting
print len(output_pages)
print len(first_in_first_out_output_fault_ratios)
plt.plot(output_pages,first_in_first_out_output_fault_ratios,label="First In First Out")
plt.plot(output_pages,least_recently_used_output_fault_ratios,label="Least Recently Used")
plt.plot(output_pages,second_chance_first_in_first_out_output_fault_ratios,label="Second Chance First In First Out")
plt.plot(output_pages,least_recently_used_minus_k_output_fault_ratios,label="Least Recently Used Minus K")
plt.plot(output_pages,preemptive_adaptive_least_recently_used_output_fault_ratios,label="Pre-emptive Adaptive Least Recently Used")
plt.plot(output_pages,average_adaptive_least_recently_used_output_fault_ratios,label="Average Adaptive Least Recently Used")
plt.plot(output_pages,least_frequently_used_output_fault_ratios,label="Least Frequently Used")
plt.plot(output_pages,ibm_output_fault_ratios,label="Adaptive Replacement Cache")
plt.legend()
plt.show()