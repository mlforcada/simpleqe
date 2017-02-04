# Trying to prepare "consensus discount" features
# Using Apertium
# MLF 20170203

# import sys
import subprocess
from nltk.tokenize import word_tokenize
import argparse
import sys
import math
import numpy as np
from scipy.optimize import minimize


def readdata(filename):
    return ((open(filename).read()).rstrip("\n")).split("\n")


# Lifted from GSoC code by Pankaj Sharma
def translateText(text, pair, directory=None):
    p1 = subprocess.Popen(['echo', text], stdout=subprocess.PIPE)
    if directory:
        p2 = subprocess.Popen(['apertium', '-d', directory, '{0}-{1}'.format(*pair)], stdin=p1.stdout, stdout=subprocess.PIPE)
    else:
        p2 = subprocess.Popen(['apertium', '{0}-{1}'.format(*pair)], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    return p2.communicate()[0].decode('utf-8').strip()

# lifted from http://stackoverflow.com/questions/10106901/elegant-find-sub-list-in-list
def subfinder(mylist, pattern):
    matches = []
    for i in range(len(mylist)):
        if mylist[i] == pattern[0] and mylist[i:i+len(pattern)] == pattern:
            matches.append(pattern)
    return matches


reload(sys)
sys.setdefaultencoding("utf-8")

# Argument parsing
parser = argparse.ArgumentParser()

# Mandatory arguments: PE time, source, MT
parser.add_argument("tr_time",help="Training PE time")
parser.add_argument("tr_source", help="Training source segments")
parser.add_argument("tr_mt", help="Training MTed segments")

#
parser.add_argument("te_time",help="Test PE time")
parser.add_argument("te_source", help="Test source segments")
parser.add_argument("te_mt", help="Test MTed segments")




# Ngram size
parser.add_argument('-m', '--maxngram', help='Maximum ngram size', type=int, default=3)

# Verbose
parser.add_argument('-v', '--verbose', help='Verbose Mode', dest="verbose", action='store_true',default=False)

# Parse them
args=parser.parse_args()

# Read the data
train_pe_time = readdata(args.tr_time)
train_source = readdata(args.tr_source)
train_mt = readdata(args.tr_mt)
test_pe_time = readdata(args.te_time)
test_source = readdata(args.te_source)
test_mt = readdata(args.te_mt)

# Zip it to loop
training_data=zip(train_pe_time,train_source,train_mt)
test_data=zip(test_pe_time,test_source,test_mt)


languagepair=("en","es")
directory="/home/mlf/apertium-sources/apertium-en-es"

# segment translations will be held in a cache
cache={}

hits = [[0 for x in range(args.maxngram+1)] for y in range(len(training_data))] 


for m, (time, source, target) in enumerate(training_data) :
#   source=train[1]
#   target=train[2]
   if args.verbose :
      print source
      print target
   source_tok=word_tokenize(source)
   target_tok=word_tokenize(target.lower())

   # Prepare long translation job to avoid starting Apertium over and over again
   # for each n-gram
   sourcesegs=""
   for n in range(1,args.maxngram+1) :
     for i in range(len(source_tok)-n+1):
       # The cache could be looked up here to avoid translating stuff --> later
       seg=" ".join(source_tok[i:i+n])
       sourcesegs= sourcesegs + seg + "\n\n"


   targetsegs=translateText(sourcesegs,languagepair,directory).lower()

   # Store n-gram translations in a cache
   for pair in zip(sourcesegs.split("\n\n"),targetsegs.split("\n\n")):
     cache[pair[0]]=pair[1]

   # I'll do the reverse cache later

      
   # Now run the thing
   hits[m][0]=len(source_tok) # Store length for zero-grams
   if args.verbose :
     print "Length=", hits[m][0]
   for n in range(1,args.maxngram+1) :
     hits[m][n]=0
     for i in range(len(source_tok)-n+1):
       seg=" ".join(source_tok[i:i+n])
       res=cache[seg]
       res_tok=word_tokenize(res.lower())
       if len(res_tok) :
          found_tok=subfinder(target_tok,res_tok)
       if found_tok : 
       #   print "( ",seg," : ", res, ")"
       #   print float(len(source_tok))/float((len(source_tok)-n+1)) 
          hits[m][n] = hits[m][n] + float(len(source_tok))/float((len(source_tok)-n+1))
     if args.verbose :
        print "Ngram=", n, " Hits=", hits[m][n]
	
# End for train



# Can I move this function definition to the top?
def mae(a) :
   MAE=0
   for m, (time, source, target) in enumerate(training_data) :
      dev=float(time)
      for n in range(0,args.maxngram+1) :
         dev=dev+a[n]*hits[m][n]
      MAE=MAE+math.fabs(dev)
   return MAE/len(training_data)
 

# Initial values --- starting with zeros for lack of a better estimate

a0=np.array([0 for y in range(args.maxngram+1)])

# Optimize to an error of 0.0001 in MAE
res = minimize(mae, a0, method='nelder-mead', options={'fatol' : 1e-4, 'disp': args.verbose})

print "Result=", res.x
print "Length coefficient=", (res.x)[0]
for n in range(1,args.maxngram+1):
   print n,"-gram coefficient=", (res.x)[n]
print "Training set MAE=", mae(res.x)



# Now compute MAE over test set

testhits = [0 for x in range(args.maxngram+1)]]

MAE=0.0

for m, (time, source, target) in enumerate(test_data) :
#   source=train[1]
#   target=train[2]
   if args.verbose :
      print source
      print target
   source_tok=word_tokenize(source)
   target_tok=word_tokenize(target.lower())

   # Prepare long translation job to avoid starting Apertium over and over again
   # for each n-gram
   sourcesegs=""
   for n in range(1,args.maxngram+1) :
     for i in range(len(source_tok)-n+1):
       # The cache could be looked up here to avoid translating stuff --> later
       seg=" ".join(source_tok[i:i+n])
       sourcesegs= sourcesegs + seg + "\n\n"


   targetsegs=translateText(sourcesegs,languagepair,directory).lower()

   # Store n-gram translations in a cache
   for pair in zip(sourcesegs.split("\n\n"),targetsegs.split("\n\n")):
     cache[pair[0]]=pair[1]

   
      
   # Now run the thing
   testhits[0]=len(source_tok) # Store length for zero-grams
   if args.verbose :
     print "Length=", testhits[0]
   for n in range(1,args.maxngram+1) :
     testhits[n]=0
     for i in range(len(source_tok)-n+1):
       seg=" ".join(source_tok[i:i+n])
       res=cache[seg]
       res_tok=word_tokenize(res.lower())
       if len(res_tok) :
          found_tok=subfinder(target_tok,res_tok)
       if found_tok : 
       #   print "( ",seg," : ", res, ")"
       #   print float(len(source_tok))/float((len(source_tok)-n+1)) 
          testhits[n] = testhits[n] + float(len(source_tok))/float((len(source_tok)-n+1))
     if args.verbose :
        print "Ngram=", n, " Hits=", testhits[n]

# Compute contribution to MAE
     dev=float(time)
     for n in range(0,args.maxngram+1) :
         dev=dev+a[n]*testhits[n]
     MAE=MAE+math.fabs(dev)/len(test_data)
# End for train

print "Test set MAE=", MAE





