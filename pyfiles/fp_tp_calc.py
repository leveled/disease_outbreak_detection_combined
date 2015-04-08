import json
import datetime
import os
import inspect
import dateutil
import random
from decimal import *
import matplotlib.pyplot as plt

def gdt(str):
    return datetime.datetime.strptime(str, "%Y-%m-%d")


#File to take warning files from subgraph files 
def makeWarningFile(path, source, co1):
	warningPath = os.path.join(path+'/input/raw/'+source+'/'+co1, 'warning_file.txt')	
	warning_file = open(warningPath, 'a')
	warning_file.seek(0)
	warning_file.truncate()	 # Deletes contents in warning file from previous use 
	
	directory = path+'/output/'+source+'/'+co1+'/subgraph'
	for filename in os.listdir(directory):
		dateobj = datetime.datetime.strptime(filename[0:10],'%Y-%m-%d').date()		
		file_path = os.path.join(directory, filename)
		items = open(file_path).read().split()
		#print items
		score = items[-1]
		for id in range(len(items)-1):							
			warning_file.write('{0} {1} {2}\n'.format(items[id], filename[0:10], score))

#Makes a list of predictions based on the warning file that Embers generates 

def makePredictionList(warning_file, cutoff):
	pred = [] # value to hold city, dt, score 
	# Proc equivalent 
	lines = open(warning_file, "r").readlines() #ADD: Open file with [id, date, score] 
	for line in lines:
		items = line.split()
		id = items[0] 
		dt = datetime.datetime.strptime(items[1], "%Y-%m-%d")
		score = float(items[2])
		if score >= cutoff:
			pred.append((id, dt, score)) #adding id, dt, score values 
			
	pred = sorted(pred, key = lambda item: item[2], reverse=True) #sorts pred value based on score
	#print pred
	#print "Predictions: "+str(len(pred))
	return pred 

			
#Makes a gsr list based off the gsr_file 

def makeGsrList(gsr_file):
	gsr = dict() #Dictionary to hold gsr events from file 
	
	for line in open(gsr_file).readlines():
		items = line.split()
		id = items[0] 
		dt = items[1] 
		
		if gsr.has_key(id):
			gsr[id][dt] = 0
		else:
			gsr[id] = {dt: 0} 
		
	#print "GSR Events: "+str(len(gsr))
	return gsr 
	
def makeGsrListNoisy(warning_file):	
	gsr = dict()
	lines = open(warning_file, "r").readlines()
	for line in lines:
		rand = random.randrange(0,10)
		items = line.split()
		if rand >= 5:
			id = items[0]
			dt = datetime.datetime.strptime(items[1], "%Y-%m-%d")
			#print "adding id: "+str(id)+" and dt: "+str(dt)
			if gsr.has_key(id):
				gsr[id][dt] = 0
			else:
				gsr[id] = {dt: 0} 
	#print gsr 
	return gsr 	

			
# TP/FP Equivalent 	

#Formula for recall is total true events within two weeks / total true events 
#Formula for true positive rate is true positive / true positive + false positive
#Formula for false positive rate is false positive days / # days 

def tpr_fp(pred, gsr, k, stdt, enddt):
	fp = 0 # number of false positives 
	tp = 0 # number of true positives 
	data = dict() # used to hold all the true events 
	n = dict() # number of events that happen within a 2 week window of all nodes 
	i = 0 
	for id, dt, score in pred:
		#print i > k
		if (i > k):
			#print "Breaking out with k of: "+str(k)+" and i of :"+ str(i)
			break
		i += 1 
		#print "Id in loop:" +str(id)
		flag = 0
		
		# First if statement checks if there is an exact match between a gsr event and an EMBERS warning
		if gsr.has_key(id) and gsr[id].has_key(dt):
			#print "True Positive with id:"+ str(id)
			data[(id,dt)] = 1
			flag = 1
			
		# Second statement to check if there is  match in the two week window 
		else: 
			#print "Are you in here?"
			nd1 = nd2 = dt 
			for j in range(7):
				nd1 = nd1 + datetime.timedelta(days=1)
				nd2 = nd2 - datetime.timedelta(days=1)
				if gsr.has_key(id) and gsr[id].has_key(nd1):
					data[(id,dt)] = 1
					flag = 1
					nd = nd1
					break  
				if gsr.has_key(id) and gsr[id].has_key(nd2):
					data[(id,dt)] = 1
					flag = 1 
					nd = nd2
					break 
				
		# Statement that increments the false positive 
		if flag == 0:
			fp = fp + 1
		# True positive here
		if flag == 1:
			nd = dt - datetime.timedelta(days = 7)
			for j in range(14):
				nd = nd + datetime.timedelta(days = 1) 
				print "Nd:+ "+str(nd)
				print "Dt:+ "+str(dt)
				if gsr[id].has_key(nd):
					print "In here"
					if not n.has_key(id):
						n[id] = dt					
				
			


	tp = len(n)
	tpr = Decimal(tp) / Decimal(len(gsr))
	fpr = Decimal(fp) / Decimal(abs((stdt - enddt).days))
	precision = len(data) / len(pred)
	#print "Test"+str(Decimal(1)/Decimal(901))
	#print "Length of prediction list: "+str(len(pred))
	#print "True Positive: "+str(tp)+" with k "+str(k) 
	#print "False Positive: "+str(fp)+" with k "+str(k)
	if (len(n) != 0):
		recall = tp / len(n) 
		return tpr, fpr, recall 

	return tpr, fpr, 0 # returns 0 for recall if it is not detected 



	
	
def graph(tprList, fprList, precisionList, filename):
	
	# Shows plot of tpr vs. fpr 
	plt.plot(tprList, fprList, '-')
	plt.xlabel('True Positive Rate')
	plt.ylabel('False Positive Rate')
	plt.show()
	
	
	plt.plot(tprList, precisionList, '-')
	plt.xlabel('Recall')
	plt.ylabel('False Positive Rate') 
	plt.show()	
	
	# x axis recall (true positive rate), y axis precision 
	# Shows plot of tpr vs. recall 
	#if not (recallList[0] == 0): # only show if there is an element in recall, edit to make more robust
		

def fp_tp_calc(cutoff, k, path, stdt, enddt, source, co1, event_Type): 
	#os.chdir('..')
	#path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
	makeWarningFile(path, source, co1)
	pred = makePredictionList(path+'/input/raw/'+source+'/'+co1+'/warning_file.txt', cutoff) 
	
	
	#		gsr = makeGsrList(os.path.join(gsrPath,filename))

	gsrPath = path+'/input/gsr'
	filename = 'Gsr_'+co1+'_'+event_Type+'.txt'
	gsr = makeGsrList(os.path.join(gsrPath, filename))	
	tprList = []
	fprList = []
	precisionList = []
	
	for i in range(1, k):
		print i
		tpr, fpr, precision = tpr_fp(pred, gsr, i, stdt, enddt)
		tprList.append(tpr)
		fprList.append(fpr)
		precisionList.append(precision)
	graph(tprList, fprList, precisionList, "")

if __name__ == '__main__':
	
	os.chdir('..')
	
	path = os.path.abspath(os.curdir)
	print path
	makeWarningFile(path)
	cutoff = 0 # change this 
	k = 100 # change this 
	pred = makePredictionList(path+'/input/warning_file.txt', cutoff) 
	
	
	gsr = makeGsrListNoisy(path+'/input/warning_file.txt')
	#print gsr
	tprList = []
	fprList = []
	recallList = []
	
	stdt  = gdt('2012-08-25')
	enddt = gdt('2012-10-29')
	
	for i in range(1,k):
		#print i
		tpr, fpr, recall = tpr_fp(pred, gsr, i, stdt, enddt)
		tprList.append(tpr)
		fprList.append(fpr)
		recallList.append(recall)
		
	print tprList
	print fprList
	print recallList
	graph(tprList, fprList, recallList, "")
	"""
	gsrPath = path+'/input/gsr_cutoff'
	
	
		
	for filename in os.listdir(gsrPath):
		gsr = makeGsrList(os.path.join(gsrPath,filename))
		tprList = []
		fprList = []
		recallList = []
		for i in range(k):
			#print i
			tpr,fpr, recall = tpr_fp(pred, gsr, i)
			tprList.append(tpr)
			fprList.append(fpr)
			recallList.append(recall)
		graph(tprList, fprList, recallList, filename) 
	"""
