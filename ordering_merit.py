# MLF 20180214
# Read:
# one sentence per line
# post-editing time (one value per line)
# post-editing time estimate (WMT result file: fields 3 and 4
# a number between zero and one
#
# Then rank according to time per length, measured and estimated,
# and compute three indicators of the merit of the estimated ranking
# 
# (1) An average, qsimple, over all ntest-1 splits of the ranking r, of
#     the ratio q_j(r) between the estimated post-editing time per unit length of 
#     the upper part [1,j] and the estimated post-editing time per unit length of the 
#     lower part [j+1,ntest], supposed to vary between q_j(opt) and 1.
# 
# (2) A per-segment normalization with respect to the optimal ranking (the sum of
#     q_j(r)-1 over [1,ntest-1] over the sum over q_j(opt)-1 over [1,ntest-1] 
#     (supposed to vary between 0 and 1.
#
# (3) A per-document average of (q_j(r)-1)/(q_j(opt)-1), supposed to vary 
#     between 0 and 1.
#
# 
# For the future: 
# perform an actual optimal ordering (Knapsack problem)
#
# 
import argparse
from nltk.tokenize import word_tokenize
import sys
import math
import numpy  # not sure I need this


reload(sys)
sys.setdefaultencoding("utf-8")

def readdata(filename):
    return ((open(filename).read()).rstrip("\n")).split("\n")
    
    
parser = argparse.ArgumentParser()
parser.add_argument("measured_time",help="Measured PE time")
parser.add_argument("estimated_time",help="Estimated indicator")
parser.add_argument("sentences", help="Sentences")
# not implemented
parser.add_argument("--intensive", action="store_true", dest="intensive", default=False, help="Estimated indicator is intensive")

args=parser.parse_args()

tmeas = readdata(args.measured_time)
sente = readdata(args.sentences)
aux = readdata(args.estimated_time)

print len(aux)
testi = [-float("inf")]*len(aux) # matrix
for i in range(len(aux)) :
	_z = aux[i].split()
	testi[int(_z[1])-1]=float(_z[2])
	
slenw=[]
slenc=[]
totlenw=0
totlenc=0
for i in range(len(sente)) :
	slenw.append(len(word_tokenize(sente[i])))
	slenc.append(len(sente[i]))
	totlenw=totlenw+len(word_tokenize(sente[i]))
	totlenc=totlenc+len(sente[i])
	
print "Total lengths: ", totlenw, " words, ", totlenc, " characters"
	
# time per unit length (word w, char c).
taumeasw=[]
tauestiw=[]	
taumeasc=[]
tauestic=[]	
tottmeas=0
for i in range(len(tmeas)) :
	taumeasw.append(float(tmeas[i])/slenw[i])
	taumeasc.append(float(tmeas[i])/slenc[i])
	if args.intensive==False :
	   tauestiw.append(float(testi[i])/slenw[i])
	   tauestic.append(float(testi[i])/slenc[i])
	else :
		tauestiw.append(float(testi[i]))   # the same for the time being
		tauestic.append(float(testi[i]))
	tottmeas=tottmeas+float(tmeas[i])

print "Total measured time: ", tottmeas, " seconds"
print "----"
print 
# For use by argsort()
ntaumeasw = numpy.array(taumeasw)
ntaumeasc = numpy.array(taumeasc)
ntauestiw = numpy.array(tauestiw)
ntauestic = numpy.array(tauestic)

# orderings (ascending)
itaumeasw = ntaumeasw.argsort()
itaumeasc = ntaumeasc.argsort()
itauestiw = ntauestiw.argsort()
itauestic = ntauestic.argsort()

# Delete this stanza
#for i in range(len(aux)) :
#   print itaumeasw[i], taumeasw[itaumeasw[i]], ntaumeasw[itaumeasw[i]]
	
# Measured times
# Minimize time for at least a certain length

# Compute q_j(r) and q_j(opt)
# for characters and words
# ugly, ugly code.

ntest=len(tmeas)
# compute for every j
qjc_r   = [0]*len(tmeas)
qjc_opt = [0]*len(tmeas)
qjw_r   = [0]*len(tmeas)
qjw_opt = [0]*len(tmeas)
 

for j in range(1,ntest): # j varies from 1 to ntest-1, as in formulas
   print "j=",j
   # upper part
   upsumtc_opt=0
   upsumtw_opt=0
   upsumlc_opt=0
   upsumlw_opt=0
   upsumtc_r=0
   upsumtw_r=0
   upsumlc_r=0
   upsumlw_r=0
   for k in range(1,j+1): # k varies from 1 to j ; indexing has to be decremented
       print "k(up)=",k
       upsumtw_opt=upsumtw_opt+float(tmeas[itaumeasw[k-1]])
       upsumtc_opt=upsumtc_opt+float(tmeas[itaumeasc[k-1]])
       upsumlc_opt=upsumlc_opt+len(sente[itaumeasc[k-1]])
       upsumlw_opt=upsumlw_opt+len(word_tokenize(sente[itaumeasw[k-1]]))
       upsumtw_r  =upsumtw_r  +float(tmeas[itauestiw[k-1]])
       upsumtc_r  =upsumtc_r  +float(tmeas[itauestic[k-1]])
       upsumlc_r  =upsumlc_r  +len(sente[itauestic[k-1]])
       upsumlw_r  =upsumlw_r  +len(word_tokenize(sente[itauestiw[k-1]]))
   uptw_r  =upsumtw_r  /upsumlw_r  
   uptc_r  =upsumtc_r  /upsumlc_r
   uptw_opt=upsumtw_opt/upsumlw_opt  
   uptc_opt=upsumtc_opt/upsumlc_opt      
   # lower part
   losumtc_opt=0
   losumtw_opt=0
   losumlc_opt=0
   losumlw_opt=0
   losumtc_r  =0
   losumtw_r  =0
   losumlc_r  =0
   losumlw_r  =0
   for k in range(j,ntest): # k varies from j+1 to ntest-1; indexing has to be decremented
       print "k(lo)=",k
       losumtw_opt=losumtw_opt+float(tmeas[itaumeasw[k-1]])
       losumtc_opt=losumtc_opt+float(tmeas[itaumeasc[k-1]])
       losumlc_opt=losumlc_opt+len(sente[itaumeasc[k-1]])
       losumlw_opt=losumlw_opt+len(word_tokenize(sente[itaumeasw[k-1]]))
       losumtw_r  =losumtw_r  +float(tmeas[itauestiw[k-1]])
       losumtc_r  =losumtc_r  +float(tmeas[itauestic[k-1]])
       losumlc_r  =losumlc_r  +len(sente[itauestic[k-1]])
       losumlw_r  =losumlw_r  +len(word_tokenize(sente[itauestiw[k-1]]))
   lotw_r  =losumtw_r  /losumlw_r  
   lotc_r  =losumtc_r  /losumlc_r
   lotw_opt=losumtw_opt/losumlw_opt  
   lotc_opt=losumtc_opt/losumlc_opt      
   # compute indicators for each j (do I need to store them?)
   qjc_r  [j]=uptc_r  /lotc_r
   qjc_opt[j]=uptc_opt/lotc_opt
   qjw_r  [j]=uptw_r  /lotw_r
   qjw_opt[j]=uptw_opt/lotw_opt
   

# now, compute the averages

Qsimplec_r  =0
Qsimplec_opt=0
Qsimplew_r  =0
Qsimplew_opt=0
Qsegw_r  =0
Qsegc_r  =0
numQdocw_r  =0
denQdocw_r  =0
numQdocc_r  =0
denQdocc_r  =0
for j in range(1,ntest):
	Qsimplec_r  =Qsimplec_r   + qjc_r  [j]/(ntest-1)
	Qsimplew_r  =Qsimplew_r   + qjw_r  [j]/(ntest-1)
	Qsimplec_opt=Qsimplec_opt + qjc_opt[j]/(ntest-1)
	Qsimplew_opt=Qsimplew_opt + qjw_opt[j]/(ntest-1)
	
	Qsegw_r + Qsegw_r + ((qjw_r  [j]-1.0)/(qjw_opt[j]-1.0))/(ntest-1)
	Qsegc_r + Qsegc_r + ((qjc_r  [j]-1.0)/(qjc_opt[j]-1.0))/(ntest-1)
	
	numQdocc_r = (qjc_r  [j]-1.0)
	denQdocc_r = (qjc_opt[j]-1.0)
	numQdocw_r = (qjw_r  [j]-1.0)
	denQdocw_r = (qjw_opt[j]-1.0)
    
Qdocc_r=numQdocc_r/denQdocc_r
Qdocw_r=numQdocw_r/denQdocw_r

print "Alignment merit figures"
print ""
print "Unnormalized measures"
print "_____________________"
print "Q_simple(r,char)=",Qsimplec_r
print "Q_simple(r,words)=",Qsimplew_r
print "Q_simple(opt,char)=",Qsimplec_opt
print "Q_simple(opt,words)=",Qsimplew_opt
print ""
print "Normalized mesaures"
print "___________________"
print "Q_seg(r,char)=",Qsegc_r
print "Q_seg(r,words)=",Qsegw_r
print "Q_doc(r,char)=",Qdocc_r
print "Q_doc(r,words)=",Qdocw_r
print ""

exit
