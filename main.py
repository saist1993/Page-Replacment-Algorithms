import os

#We need to read from a file and save the parsed meta data in an list .
#Let all the temporary variable begin with "_" that is underscore 
input = []
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
	def __init__(self, number, size, mapped, startLocation):
		self.size=size
		self.mapped=mapped
		self.Location=startLocation
		self.number=number

#lets make a virtual memory table and a mapping function 

virtualMemory = []
ram=[]

def fillVirtualMemory(pageSize,vMemorySize):
	virtualPageNo=0
	#print pageSize
	for memoryLocation in range(0,vMemorySize, pageSize):
		#print memoryLocation
		virtualPage = Page(virtualPageNo, pageSize, -1, memoryLocation)
		virtualMemory.append(virtualPage)
		virtualPageNo=virtualPageNo + 1


fillVirtualMemory(4,64)
for x in range(0,4):		 	
	print virtualMemory[x].Location


#need to write a converter basically mmu which will map the virtual process to memory location ..

def mmu(processId, function, location):
	location= 









readFile("/home/gaurav/OperatingSystem/Project/example_trace.txt")