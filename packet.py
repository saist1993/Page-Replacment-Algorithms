import statistics
input1 = [1,2,3,4,5,1,2,3,4,5,1,2,3,4,5]
def unique(i,input, unique_array):
	if input[i] in unique_array:
		return
	else:
		unique_array.append(input[i])
		return True	

def main1(input,virtualMemory,count,mode):
	unique_array = []
	for i in range(len(input)):
		k = unique(i,input,unique_array)
		if k:
			array = []
			counter=0
			for index in range(i,len(input)):
				if input[i]==input[index]:
					array.append(counter)
					counter = 0
				counter +=1	
			#print "the mode is " + str(statistics.mode(array))
			mode.append(statistics.mode(array))	
			count[input[i]]=array

def prediction(input,virtualMemory):
	count = {}
	mode = []
	main1(input,virtualMemory,count,mode)
	
	k= statistics.mode(mode)
	factor=int(virtualMemory)*.1
	if k>virtualMemory:
		print "yo"
		return 'least_recentlt_used_minus_k', k

	elif mode < factor:
		print "ho" 
		return 'first_in_first_out'

	else:
		print "bo"
		return 'ibm'


#predection(input1,4)