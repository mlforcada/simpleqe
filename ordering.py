# MLF 20171228
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
parser.add_argument("estimated_time",help="Estimated indicator")
parser.add_argument("sentences", help="Sentences")
parser.add_argument("fraction", type=float, help="Fraction")
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

# orderings (ascending
itaumeasw = ntaumeasw.argsort()
itaumeasc = ntaumeasc.argsort()
itauestiw = ntauestiw.argsort()
itauestic = ntauestic.argsort()

# Delete this stanza
#for i in range(len(aux)) :
#   print itaumeasw[i], taumeasw[itaumeasw[i]], ntaumeasw[itaumeasw[i]]
	
# Measured times
# Minimize time for at least a certain length

# Words
print "Best time for a given length in words"
l = 0
t = 0
for i in range(len(aux)) :
	l=l+len(word_tokenize(sente[itaumeasw[i]]))
	t=t+float(tmeas[itaumeasw[i]])
	if l>args.fraction*totlenw : # if a certain length is reached, break
		break
print "Total length= ", l, " words"
print "Measured time= ", t, " seconds"
tmeasw=t

# Characters
print "Best time for a given length in characters"
l = 0
t = 0
for i in range(len(aux)) :
	l=l+len(sente[itaumeasc[i]])
	t=t+float(tmeas[itaumeasc[i]]) 
	if l>args.fraction*totlenc : # if a certain length is reached, break
		break
print "Total length= ", l, " characters" 
print "Best measured time= ", t, " seconds"
tmeasc=t

# Minimize time for at least a certain length
print "Best length in words for less than a total time"
l = 0
t = 0
for i in range(len(aux)) :
	if t>args.fraction*tottmeas : # never arrive to the limit time
		break
	l=l+len(word_tokenize(sente[itaumeasw[i]]))
	t=t+float(tmeas[itaumeasw[i]]) 
print "Total time= ", t, " seconds"
print "Best length=", l, " words"
lmeasw=l
	
# Minimize time for at least a certain length
print "Best length in characters for less than a total time"
l = 0
t = 0
for i in range(len(aux)) :
	if t>args.fraction*tottmeas : # never arrive to the limit time
		break
	l=l+len(sente[itaumeasc[i]])
	t=t+float(tmeas[itaumeasc[i]]) 
print "Total time= ", t, " seconds"
print "Best length=", l, " characters"
lmeasc=l

print "--------------------------------------------------------"
print "Estimated times"
print ""
# Estimated times ###########
# Minimize time for at least a certain length
# Words
print "Best estimated time for a given length in words"
l = 0
t = 0
for i in range(len(aux)) :
	l=l+len(word_tokenize(sente[itauestiw[i]]))
	t=t+float(tmeas[itauestiw[i]])
	if l>args.fraction*totlenw : # if a certain length is reached, break
		break
print "Total length= ", l, " words"
print "Measured time= ", t, " seconds"
testiw=t

# Characters
print "Best estimated time for a given length in characters"
l = 0
t = 0
for i in range(len(aux)) :
	l=l+len(sente[itauestic[i]])
	t=t+float(tmeas[itauestic[i]]) 
	if l>args.fraction*totlenc : # if a certain length is reached, break
		break
print "Total length= ", l, " characters" 
print "Best measured time= ", t, " seconds"
testic=t

# Minimize time for at least a certain length
print "Best estimated length in words for less than a total time"
l = 0
t = 0
for i in range(len(aux)) :
	if t>args.fraction*tottmeas : # never arrive to the limit time
		break
	l=l+len(word_tokenize(sente[itauestiw[i]]))
	t=t+float(tmeas[itauestiw[i]])
print "Total time= ", t, " seconds"
print "Best length=", l, " words"
lestiw=l
	
# Minimize time for at least a certain length
print "Best length in characters for less than a total time"
l = 0
t = 0
for i in range(len(aux)) :
	if t>args.fraction*tottmeas : # never arrive to the limit time
		break
	l=l+len(sente[itauestic[i]])
	t=t+float(tmeas[itauestic[i]]) 
print "Total time= ", t, " seconds"
print "Best length=", l, " characters"
lestic=l

# Print splits

print ""
print "Current fraction=", args.fraction
print "Splits"
print "Best time, words; meas=", tmeasw/tottmeas , " esti=", testiw/tottmeas
print "Best time, chars; meas=", tmeasc/tottmeas , " esti=", testic/tottmeas
print "Best use of time, words; meas=", float(lmeasw)/totlenw, " esti=", float(lestiw)/totlenw
print "Best use of time, chars; meas=", float(lmeasc)/totlenc, " esti=", float(lestic)/totlenc



