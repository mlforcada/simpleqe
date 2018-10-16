# MLF 20180218
# Read:
# one sentence per line
# post-editing time (one value per line)
# post-editing time estimate (WMT result file: fields 3 and 4
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
# (3) A per-document normalization (Q_simple(r)-1)/(Q_simple(opt)-1), also supposed to vary 
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
import numpy 

reload(sys)
sys.setdefaultencoding("utf-8")

def readdata(filename):
    return ((open(filename).read()).rstrip("\n")).replace("\r","").split("\n")

def taus(tmeas, slen, taumeas, tauesti):
    for i in range(len(tmeas)) :
        taumeas.append(float(tmeas[i])/slen[i])
        if args.intensive==False :
                tauesti.append(float(testi[i])/slen[i])
        else :
                tauesti.append(float(testi[i]))   # the same for the time being

def q_parts(idx1, idx2, itau, tmeas, slen):
   sumt=0
   suml=0
   for k in range(idx1,idx2): # k varies from 1 to j ; indexing has to be decremented
       sumt+=float(tmeas[itau[k-1]])
       suml+=slen[itau[k-1]]
   return sumt/suml

parser = argparse.ArgumentParser()
parser.add_argument("measured_time",help="Measured PE time")
parser.add_argument("estimated_time",help="Estimated indicator")
parser.add_argument("sentences", help="Sentences")
# not implemented
parser.add_argument("--intensive", action="store_true", dest="intensive", default=False, help="Estimated indicator is intensive")

args=parser.parse_args()

tmeas = numpy.array(readdata(args.measured_time), dtype=float)
sente = readdata(args.sentences)
aux = readdata(args.estimated_time)

print "Number of segments=", len(aux)
testi = [-float("inf")]*len(aux) # matrix
for i in range(len(aux)) :
	_z = aux[i].split()
	testi[int(_z[1])-1]=float(_z[2])
	
slenw=[]
slenc=[]
totlenw=0
totlenc=0
for s in sente:
	slenw.append(len(word_tokenize(s)))
	slenc.append(len(s))
totlenw+=sum(slenw)
totlenc+=sum(slenc)
	
print "Total lengths: ", totlenw, " words, ", totlenc, " characters"
	
# time per unit length (word w, char c).
taumeasw=[]
tauestiw=[]
taus(tmeas,slenw,taumeasw, tauestiw)

taumeasc=[]
tauestic=[]
taus(tmeas,slenc,taumeasc, tauestic)

tottmeas=sum(tmeas)

print "Total measured time: ", tottmeas, " seconds"
print "----"
print 

# orderings (ascending)
itaumeasw = numpy.array(taumeasw).argsort()
itaumeasc = numpy.array(taumeasc).argsort()
itauestiw = numpy.array(tauestiw).argsort()
itauestic = numpy.array(tauestic).argsort()


# Compute q_j(r) and q_j(opt)
# for characters and words
# ugly, ugly code.

ntest=len(tmeas)
# compute for every j from 1 to ntest-1 (0 not used).
qjc_r   = [0]*ntest
qjc_opt = [0]*ntest
qjw_r   = [0]*ntest
qjw_opt = [0]*ntest

for j in range(1,ntest): # j varies from 1 to ntest-1, as in formulas
   # upper part
   uptw_r  =q_parts(1,j+1,itauestiw,tmeas,slenw)
   uptc_r  =q_parts(1,j+1,itauestic,tmeas,slenc)
   uptw_opt=q_parts(1,j+1,itaumeasw,tmeas,slenw)
   uptc_opt=q_parts(1,j+1,itaumeasc,tmeas,slenc)

   # lower part
   lotw_r  =q_parts(j+1,ntest+1,itauestiw,tmeas,slenw)
   lotc_r  =q_parts(j+1,ntest+1,itauestic,tmeas,slenc)
   lotw_opt=q_parts(j+1,ntest+1,itaumeasw,tmeas,slenw)
   lotc_opt=q_parts(j+1,ntest+1,itaumeasc,tmeas,slenc)
           
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
for j in range(1,ntest):  # j varies from 1 to ntest-1 as in previous main loop
	Qsimplec_r   += qjc_r  [j]/(ntest-1.0)
	Qsimplew_r   += qjw_r  [j]/(ntest-1.0)
	Qsimplec_opt += qjc_opt[j]/(ntest-1.0)
	Qsimplew_opt += qjw_opt[j]/(ntest-1.0)
	
	Qsegw_r += ((qjw_r[j]-1.0)/(qjw_opt[j]-1.0))/(ntest-1)
	Qsegc_r += ((qjc_r[j]-1.0)/(qjc_opt[j]-1.0))/(ntest-1)

print "Alignment merit figures"
print ""
print "Unnormalized measures"
print "_____________________"
print "Q_simple(r,char)=",Qsimplec_r
print "Q_simple(r,words)=",Qsimplew_r
print "Q_simple(opt,char)=",Qsimplec_opt
print "Q_simple(opt,words)=",Qsimplew_opt
print ""
print "Normalized measures"
print "___________________"
print "Q_seg(r,char)=",Qsegc_r
print "Q_seg(r,words)=",Qsegw_r
print "Q_doc(r,char)=",(Qsimplec_r-1.0)/(Qsimplec_opt-1.0)
print "Q_doc(r,words)=",(Qsimplew_r-1.0)/(Qsimplew_opt-1.0)
