import os
import json
import pickle
import datetime 
import os
import time
import multiprocessing
from utils import normalize_str as nstr


def gdt(str):
    return datetime.datetime.strptime(str, "%Y-%m-%d")

def keyterms(database, cutoff):
    kws = dict()
    for (ci, co, st), dt_tms in database.items():
        for dt, tms in dt_tms.items():
            for tm, f in tms.items():
                if kws.has_key(tm):
                    kws[tm] = kws[tm] + f
                else:
                    kws[tm] = f
    keytms = dict()
    for tm, f in kws.items():
        if f > cutoff:
            keytms[tm] = f
    return keytms

def extend_gsr_dt(gsr_dt, r):
    ext_gsr_dt = dict()
    for dt in gsr_dt:
        ext_gsr_dt[dt] = 1
        for i in range(r):
            dt = dt + datetime.timedelta(days=1)
            ext_gsr_dt[dt] = 1
    for dt in gsr_dt:
        for i in range(r):
            dt = dt - datetime.timedelta(days=1)
            ext_gsr_dt[dt] = 1
    return ext_gsr_dt

# kws refers to the list of keywords whose frequencies are equal to or greater than a predefined cutoff
# dt_kws: {dt: {kw: freq}}
# gsr_dt: a list of datetimes
def pvalues_calc(id, dt_cnt, gsr_dt, stdt, cutdt, enddt):
    gsr_dt = extend_gsr_dt(gsr_dt, 7)
    days = (enddt - stdt).days + 1
    pvalues = dict()
    dt = stdt - datetime.timedelta(days = 1)
    vec = []
    #print 'start ----------------------------------'
    while dt < cutdt:
        #print dt
        dt = dt + datetime.timedelta(days = 1)
        if dt_cnt.has_key(dt):
            c = dt_cnt[dt] # refers to the count of keyword kw in day dt
        else:
            c = 0
        if not gsr_dt.has_key(dt):
            vec.append(c)
        else:
            print '***************'+str(dt)
    length = (cutdt - stdt).days
    p_ref = len(vec) * 1.0 / length
    dt = cutdt - datetime.timedelta(days = 1)
    #print '############################################'
    while dt <= enddt:
        #print dt
        dt = dt + datetime.timedelta(days = 1)
        if dt_cnt.has_key(dt):
            c = dt_cnt[dt]
            fp = [tm for tm in vec if tm >= c]
            if len(vec) > 0:
                pvalue = len(fp) / (len(vec) * 1.0)
                if c <= 5:
                    pvalue = 0.5
            else:
                pvalue = 1
        else:
            c = 0
            pvalue = 1.0
        if pvalue > p_ref:
            pvalue = p_ref
        pvalues[dt] = pvalue
     #   print pvalue
    #for dt, pvalue in pvalues.items():
    #    print dt, pvalue
    if id == 45:
        f = open('log.txt', 'w')
        for dt, pvalue in sorted(pvalues.items(), key = lambda item: item[0]):
            f.write('{0}, {1}'.format(dt, pvalue) + '\n')
 #           print dt,pvalue
        f.close()
    return pvalues

def mainproc(co1,gsrName,databaseName,stdt,cutdt,enddt, path, source):
    
    # Establish communication queues

    folder = path+'/input/'
    outputFolderName= path+'/output/'+source+'/'+co1+'/pvalue'


    for file in os.listdir(outputFolderName):
		file_path = os.path.join(outputFolderName, file)
		try: 
			if os.path.isfile(file_path):
				os.unlink(file_path)
		except Exception, e:
			print e    
    
    
    savePathTemp = path+'/input/ci2d'
    coTemp = co1+'_ci_2_id.txt'
    pathName = os.path.join(savePathTemp, coTemp)

    ci_2_id = json.loads(open(pathName).read())



    gsr = pickle.loads(open(os.path.join(folder+'/gsr', gsrName)).read())
 #   //print gsr
#    for co1 in cos[:]:
  #  ci_2_id = json.loads(open('data/{0}/ci_2_id.txt'.format(co1)).read())
    
    co_pvalues = dict()

    database = pickle.loads(open(os.path.join(path+'/output/'+source+'/'+co1, databaseName)).read())
 #       print database
    cis = database.keys()
    for (ci, co, st) in cis:
        ci = nstr(ci)
        co = nstr(co)
        st = nstr(st)
        dt_cnt = database[(ci, co, st)]
        if not gsr.has_key((ci, co, st)):
            gsr[(ci, co, st)] = dict()
        gsr_dt = gsr[(ci, co, st)]
        str = ci + '_' + co + '_' + st
        if ci_2_id.has_key(str):
            id = ci_2_id[str]
        else:
            id = -1
        pvalues = pvalues_calc(id, dt_cnt, gsr_dt, stdt, cutdt, enddt)
        #print pvalues
        co_pvalues[(ci, co, st)] = pvalues

    dt = cutdt - datetime.timedelta(days=1)
    while dt < enddt:
        print dt
        dt = dt + datetime.timedelta(days = 1)
        dt_data = []
        for (ci, co, st), pvalues in co_pvalues.items():
             cistr = ci + '_' + co + '_' + st
        #print co_pvalues.items()
             if ci_2_id.has_key(cistr):
                id = ci_2_id[cistr]
                dt_data.append([id, pvalues[dt]])
             else:
                dt_data = sorted(dt_data, key = lambda item: item[0])
        
        n = len(ci_2_id.keys())
        dt_data1 = []
        for i in range(n):
            dt_data1.append([i, 1.0])
        for id, p in dt_data:
            dt_data1[id] = [id, p]
            #print id,p
        #folder1 = folderPath+'{0}/'.format(co1)+outputFolderName
        if not os.path.exists(outputFolderName):
            os.makedirs(outputFolderName)
        out = open(os.path.join(outputFolderName, '{0}.txt'.format(dt.strftime("%Y-%m-%d"))), 'w')
        for id, p in dt_data1:
           # print p
            out.write('{0} {1}'.format(id, p) + '\n')
        out.close()
'''
if __name__ == '__main__':
    cos = [ 'chile']
    for co1 in cos:
        folderPath='data/'
        gsrName='cu_gsr.txt'
        ci_2_idName='data/{0}/ci_2_id.txt'.format(co1)
        databaseName='{0}_twitter_cnt_data.txt'.format(co1)
        outputFolderName='twitter_output'
        stdt  = gdt('2012-08-25')
        cutdt = gdt('2012-08-27')
        enddt = gdt('2012-08-29')
        mainproc(co1,folderPath,gsrName,ci_2_idName,databaseName,outputFolderName,stdt,cutdt,enddt)
'''

 
