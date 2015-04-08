import os
import json
import datetime
import pickle
import inspect
from sys import argv
from utils import normalize_str as nstr

#script, gsrfile = argv 

def gdt(str):
    return datetime.datetime.strptime(str, "%Y-%m-%d")

def deletePreviousOutput(path):
	for file in os.listdir(path+"/input/gsr"):
			file_path = os.path.join(path, file)
			try: 
				if os.path.isfile(file_path):
					os.unlink(file_path)
			except Exception, e:
				print e

def generateGsr(gsrfile, co1, eventTypes):
	path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory	
	gsrfile1 = os.path.join(path, gsrfile)
	events = [json.loads(line) for line in open(gsrfile1).readlines()] #Loads all events from the gsr file
	gsr = dict()

	
	for event in  events[:]:
		et = event['eventType']
		if et in eventTypes:
			(co, st, ci) = event['location']
			if co and st and ci and co != '-' and st != '-' and ci != '-':
				co = nstr(co).lower()
				st = nstr(st).lower()
				ci = nstr(ci).lower()
				dtstr = event['eventDate'][:10]
				dt = datetime.datetime.strptime(dtstr, "%Y-%m-%d")
	
				# Checks if the key (ci, co, st, et) is in gsr, otherwise adds it to the dictionary
				if not gsr.has_key((ci, co, st, et)): 
					gsr[(ci, co, st, et)] = {dt: 1}
				else:        			
					gsr[(ci, co, st, et)][dt] = 1 
	return gsr 
			
def generateGsrPkl(path, gsr):	
	for key in gsr: 
		#Writes files to unique gsr text file 
 
		pathName = os.path.join(path+"/input/gsr", str(key[1])+'_'+str(key[3])+'_gsr.txt')
		print 'Writing to: '+str(key[1])+'_'+str(key[3])+'_gsr.txt'
		open(pathName, 'a').write(pickle.dumps(gsr[key]))
#		print 'Writing: '+str(key[1])+'_'+str(key[3])+'_gsr.txt'
	
	
def generateGsrCutoff(path, co1, gsr, cutdt, enddt):		
	pathName = os.path.join(path+"/input/ci2d", co1+'_ci_2_id.txt')
	ci_2_id = json.loads(open(pathName).read())
	items = sorted(ci_2_id.keys())

	for (ci, co, st, et), dts in gsr.items():
		if co == co1:
			ci = ci + '_' + co + '_' + st
			if ci_2_id.has_key(ci):
				id = ci_2_id[ci]
				for dt in sorted(dts):
					if dt >= cutdt and dt <= enddt: 
						print 'Writing to: Gsr_'+co+'_'+et+'.txt'
						pathName = os.path.join(path+"/input/gsr", 'Gsr_'+co+'_'+et+'.txt')
						#pathName = os.path.join(path+'
						open(pathName, 'a').write('{0} {1}\n'.format(id, dt.strftime('%Y-%m-%d'))) 
						
						#print 'Writing: '+'{0} {1}\n'.format(id, dt.strftime('%Y-%m-%d')  


def gsr(co1, eventTypes, gsrfile, cutdt, enddt):
	#print os.path.abspath(os.curdir) 
	os.chdir('..')
	path = os.path.abspath(os.curdir)
	print path
	deletePreviousOutput(path)
	gsr = generateGsr(gsrfile, co1, eventTypes)
	generateGsrPkl(path, gsr)
	generateGsrCutoff(path, co1, gsr, cutdt, enddt)


"""
if __name__ == '__main__':

	gsrfile = 'gsrFebruary_all.mjson' 
	os.chdir('..')
	path = os.path.abspath(os.curdir)
	#path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
	deletePreviousOutput(path)
	
	#take cutdt, enddt, cos, event types
	cutdt = gdt('2013-12-31') #cutoff date 
	enddt = gdt('2015-03-29') #end date 
	cos = ['ecuador', 'argentina', 'chile', 'mexico', 'colombia'] #List of countries 
	eventTypes = ['0311', '0312', '0313', '0314'] #List of events 
	col = 'chile'
	gsr = generateGsr(gsrfile, cos, eventTypes)
	generateGsrPkl(path, gsr)
	generateGsrCutoff(path, col, gsr, cutdt, enddt)
"""