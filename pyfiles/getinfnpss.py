import os
import sys
import random
import json
import math
from os.path import join
from math import log
import sys
sys.setrecursionlimit(10000)
########################################
#
#  return {date:[[subgraph], F-socre]}
#
#######################################

def npss_detection(place, E, alpha_max):
    K = 5
    V = []
    for site, pv in place.items():
        V.append([site, pv])
    V = [V]

    C = len(V)
    total_entity = 0
    for lt in V:
        total_entity = total_entity + len(lt)
    Z = int(log(total_entity+1))
    S_STAR = []
    epislon = 0.000001

    def quicksort(L):
        if len(L) > 1:
            pivot = random.randrange(len(L))
            elements = L[:pivot]+L[pivot+1:]
            left = [element for element in elements if element[1] < L[pivot][1]]
            right = [element for element in elements if element[1] >= L[pivot][1]]
            return quicksort(left) + [L[pivot]] + quicksort(right)
        return L

    for i in range(C):
        V[i] = quicksort(V[i])

    for k in range(K):
        for c in range(C):
            if len(V[c]) < k + 1:
                continue

            S = []
            v0 = V[c][k][0]
            S.append(v0)
            S_phi = log(1/(V[c][k][1] + epislon) + epislon)

            for z in range(Z):
                G = []
                for te in V:
                    for v in te:
                        if v[0] not in S:
                            for e in S:
                                if E.has_key(str(v[0]) + '_' + str(e)) or E.has_key(str(e) + '_' + str(v[0])):
                                    G.append(v)
                G = quicksort(G)
                phi = []
                for i in range(len(G)):
                    N = i + 1
                    max_phi = -1.0

                    for j in range(N):
                        if G[j][1] < alpha_max:
                            a = (j+1)*1.0/N
                            b = G[j][1]
                            s_phi = N * (a * log(epislon + a/(b+epislon)) + (1-a)*log(epislon + (1-a)/(1-b+epislon)))
                            if s_phi > max_phi:
                                max_phi = s_phi
                    phi.append(max_phi)

                if len(phi) > 0 and max(phi) > S_phi:
                    S_phi = max(phi)

                B = [] + S
                if len(phi) > 0 and max(phi) > 0:
                    max_phi = max(phi)
                    for i in range(phi.index(max_phi)+1):
                        if G[i][0] not in B:
                            B.append(G[i][0])

                if len(B) - len(S) != 0:
                    S = B
                else:
                    break
            item = []
            item.append(S)
            item.append(S_phi)
            S_STAR.append(item)

    S_STAR = quicksort(S_STAR)
    if len(S_STAR) > 0:
        return S_STAR[len(S_STAR)-1]
    else:
        return None

def getinfnpss(pvalue, network, alpha_max):
    subgraph = {}

    for eventdate, place in pvalue.items():
        S_STAR = npss_detection(place, network, alpha_max)
        if S_STAR:
            subgraph[eventdate] = S_STAR
    
    return subgraph

    

def getinfnpss_f(alpha_max,graphfile, path, source, co1):
    pvaluefolder=path+'/output/'+source+'/'+co1+'/pvalue'
    subgraphfolder =  path+'/output/'+source+'/'+co1+'/subgraph'
    
#    files = [file for file in os.listdir(folder) if file.find(co1) >= 0]
    files = [file for file in os.listdir(pvaluefolder)]
    for file in files[:]:
   #     print file
        pvalue = {}
        for line in open(os.path.join(pvaluefolder, file)).readlines():
           
          #  pvalue={}
          #  pvalue['2012-08-27.txt']=
            item = line.split()
            pvalue[int(item[0])] = float(item[1])
        
        network = {}
        for line in open(graphfile).readlines():
            item = line.split()
            edge = '{0}_{1}'.format(item[0], item[1])
            network[edge] = float(item[2])
        
        print 'Result subgraph: '
        print npss_detection(pvalue, network, alpha_max)
        '''
        for i in range(50):
            pvalue[i] = 0.01
    
        print 'Result 2: '
        
        print npss_detection(pvalue, network, alpha_max)
        '''

        result=npss_detection(pvalue, network, alpha_max)

        if not os.path.exists(subgraphfolder):
            os.makedirs(subgraphfolder)
        out = open(os.path.join(subgraphfolder, '{0}'.format(file)), 'w')
          
   
        for i in range(len(result[0])):            
            out.write('{0}'.format(result[0][i]) + ' ')
        out.write('{0}'.format(result[1]))
       # out.write('{0}'.format(result))
        out.close()

'''    
if __name__ =='__main__':

  #  pvalue = {'2013-02-04':{0: 1, 1: 0.005, 2: 0.005, 3: 0.01, 4: 0.002}, '2013-02-05':{0: 0.01, 1: 0.05, 2: 0.9, 3: 0.1, 4: 0.002}}
  #  network = {'0_1': 0.2, '1_2': 0.1, '2_0': 0.2, '2_3': 0.2, '3_4': 0.2}
    alpha_max = 1
    folder = 'blogs_output'
    subgraphfolder = 'subraph'
    graphfile='chile_k_25_graph.txt'
    getinfnpss_f(alpha_max,folder,subgraphfolder,graphfile)
  #  print pvalue.items()[0][1]
  #  print npss_detection(pvalue.items()[0][1], network, alpha_max)
'''   