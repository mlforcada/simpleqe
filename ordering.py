# MLF 20171226
# Read:
# one sentence per line
# post-editing time (one value per line)
# post-editing time estimate (WMT result file: fields 3 and 4
# a number between zero and one
#
# Then rank according to time per length, measured and estimated,
# and compute:
# The total time (according to the ranking) for the best sentences
# up to a certain length or longer
# The total length (according to the ranking) for the best sentences 
# up to a certain total time or shorter
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
parser.add_argument("estimated_time",help="Estimated PE time")
parser.add_argument("sentences", help="Sentences")
parser.add_argument("fraction", type=float, help="Fraction")
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
	
# time per unit length (word w, char c).
taumeasw=[]
tauestiw=[]	
taumeasc=[]
tauestic=[]	
tottmeas=0
tottesti=0
for i in range(len(tmeas)) :
	taumeasw.append(float(tmeas[i])/slenw[i])
	taumeasc.append(float(tmeas[i])/slenc[i])
	tauestiw.append(float(testi[i])/slenw[i])
	tauestic.append(float(testi[i])/slenc[i])
	tottesti=tottesti+float(testi[i])
	tottmeas=tottmeas+float(tmeas[i])

# For use by argsort()
ntaumeasw = numpy.array(taumeasw)
ntaumeasc = numpy.array(taumeasc)
ntauestiw = numpy.array(tauestiw)
ntauestic = numpy.array(tauestic)

# orderings (ascending
itaumeasw = ntaumeasw.argsort()
itaumeasc = ntaumeasc.argsort()
itauestiw = ntauestiw.argsort()
itauestic = ntauestic.argsort()
	
# Measured times
# Minimize time for at least a certain length

# Words
print "Best time for a given length in words"
l = 0
t = 0
for i in itaumeasw :
	l=l+len(sente[itaumeasw[i]])
	t=t+float(tmeas[itaumeasw[i]]) 
	if l>args.fraction*totlenw : # if a certain length is reached, break
		break
print "Total length= ", l, " words"
print "Measured time= ", t, " seconds"

# Characters
print "Best time for a given length in characters"
l = 0
t = 0
for i in itaumeasc :
	l=l+len(sente[itaumeasc[i]])
	t=t+float(tmeas[itaumeasc[i]]) 
	if l>args.fraction*totlenc : # if a certain length is reached, berak
		break
print "Total length= ", l, " words" 
print "Best measured time= ", t, " seconds"

# Minimize time for at least a certain length
print "Best length in words for less than a total time"
l = 0
t = 0
for i in itaumeasw :
	if t>args.fraction*tottmeas : # never arrive to the limit time
		break
	l=l+len(sente[itaumeasw[i]])
	t=t+float(tmeas[itaumeasw[i]]) 
print "Total time= ", t, " seconds"
print "Best length=", l, " words"

	
# Minimize time for at least a certain length
print "Best length in characters for less than a total time"
l = 0
t = 0
for i in itaumeasc :
	if t>args.fraction*tottmeas : # never arrive to the limit time
		break
	l=l+len(sente[itaumeasc[i]])
	t=t+float(tmeas[itaumeasc[i]]) 
print "Total time= ", t, " seconds"
print "Best length=", l, " characters"


print "--------------------------------------------------------"
print "Estimated times"
print ""
# Estimated times ###########
# Minimize time for at least a certain length
# Words
print "Best estimated time for a given length in words"
l = 0
t = 0
for i in itauestiw :
	l=l+len(sente[itauestiw[i]])
	t=t+float(tmeas[itauestiw[i]])
	if l>args.fraction*totlenw : # if a certain length is reached, break
		break
print "Total length= ", l, " words"
print "Measured time= ", t, " seconds"

# Characters
print "Best estimated time for a given length in characters"
l = 0
t = 0
for i in itauestic :
	l=l+len(sente[itauestic[i]])
	t=t+float(tmeas[itauestic[i]]) 
	if l>args.fraction*totlenc : # if a certain length is reached, berak
		break
print "Total length= ", l, " words" 
print "Best measured time= ", t, " seconds"

# Minimize time for at least a certain length
print "Best estimated length in words for less than a total time"
l = 0
t = 0
for i in itauestiw :
	if t>args.fraction*tottmeas : # never arrive to the limit time
		break
	l=l+len(sente[itauestiw[i]])
	t=t+float(tmeas[itauestiw[i]])
print "Total time= ", t, " seconds"
print "Best length=", l, " words"

	
# Minimize time for at least a certain length
print "Best length in characters for less than a total time"
l = 0
t = 0
for i in itaumeasc :
	if t>args.fraction*tottmeas : # never arrive to the limit time
		break
	l=l+len(sente[itauestic[i]])
	t=t+float(tmeas[itauestic[i]]) 
print "Total time= ", t, " seconds"
print "Best length=", l, " characters"




