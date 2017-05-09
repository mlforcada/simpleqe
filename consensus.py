# Trying to prepare "consensus discount" features
# Using Apertium
# MLF 20170505

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
parser.add_argument('--maxngram', help='Maximum ngram size', type=int, default=3)
# Verbose
parser.add_argument('-v', '--verbose', help='Verbose Mode', dest="verbose", action='store_true',default=False)

# Optimization
parser.add_argument('--maxiter', help="Maximum number of iterations (default 200)", type=int, default=200)

# Repeats
parser.add_argument('--repeats', help="Number of repeats", type=int, default=10)

# Counts
# By default, multiple hits are taken as a Boolean value
# This option actually counts the hits
parser.add_argument('--counts', help="Count hits instead of Boolean", action="store_true", default=False)


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

# Store the hits for each n-gram size and each segment
hits = [[0 for x in range(args.maxngram+1)] for y in range(len(training_data))] 

# To count the training set coverage ratio
attempts = [0 for x in range(args.maxngram+1)]
successes = [0 for x in range(args.maxngram+1)]


for m, (time, source, target) in enumerate(training_data) :
#   source=train[1]
#   target=train[2]
   if args.verbose :
      print "=========== segment {0}".format(m)
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
       try :  # this should not be needed
          res=cache[seg]
       except KeyError:
          res="Dummy Dummy Dummy"
          if args.verbose :
             print "==== KeyError exception handled when querying cache during the training phase"
             print "Key=[[["+seg+"]]]"
       res_tok=word_tokenize(res.lower())
       attempts[n] = attempts[n] + 1  # matching attempts for n-gram size n
       if len(res_tok) :
          found_tok=subfinder(target_tok,res_tok)
       if found_tok : 
       #   print "( ",seg," : ", res, ")"
       #   print float(len(source_tok))/float((len(source_tok)-n+1))
          if args.counts :
             successes[n] = successes[n] + len(found_tok)
             hits[m][n] = hits[m][n] + float(len(source_tok))/float((len(source_tok)-n+1)) * len(found_tok)
          else : 
             successes[n] = successes[n] + 1
             hits[m][n] = hits[m][n] + float(len(source_tok))/float((len(source_tok)-n+1))
     if args.verbose :
        print "Ngram=", n, " Hits=", hits[m][n]
	
# End for train

if args.verbose :
   for key in cache :
      print "((( " + key + " ::: " + cache[key] + ")))"


# Can I move this function definition to the top?
def mae(a) :
   MAE=0
   for m, (time, source, target) in enumerate(training_data) :
      dev=float(time)
      for n in range(0,args.maxngram+1) :
         dev=dev-a[n]*hits[m][n]
      MAE=MAE+math.fabs(dev)
   return MAE/len(training_data)
 
best_train_set_MAE=float("inf")
for i in range(args.repeats) :

  # Initial values --- starting with a value sampled from N(0,1)
  a0=np.array([np.random.randn() for y in range(args.maxngram+1)])

  # Optimize to an error of 0.00001 in MAE (will change later, can also use    BFGS)
  result = minimize(mae, a0, method='nelder-mead', options={'fatol' : 1e-6, 'disp' : True, 'maxiter' : args.maxiter})

  if result.success :
     print "Optimization successful in {0} iterations".format(result.nit) 
  else : 
     print "Optimization unsuccessful"
     print result.status



  print "Result=", result.x
  print "Length coefficient=", (result.x)[0]
  for n in range(1,args.maxngram+1):
   print n,"-gram coefficient=", (result.x)[n]
   print n,"-gram success rate=", float(successes[n])/float(attempts[n])
   
  current_MAE=mae(result.x)
  print "Training set MAE=", current_MAE
  if current_MAE<best_train_set_MAE :
     best_train_set_MAE = current_MAE
     best_a=result.x
     print "Best training set MAE so far=", best_train_set_MAE

# End for

# Now compute MAE over test set

testhits = [0 for x in range(args.maxngram+1)]

# To count the test set coverage ratio
attempts = [0 for x in range(args.maxngram+1)]
successes = [0 for x in range(args.maxngram+1)]


MAE=0.0

for m, (time, source, target) in enumerate(test_data) :
#   source=test[1]
#   target=test[2]
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
       try : # This should not be necessary, but avoids some (strange) KeyErrors
          res=cache[seg]
       except KeyError : 
          res="Dummy Dummy Dummy"
          if args.verbose :
             print "==== KeyError exception handled when querying cache during the test phase"
             print "Key=[[["+seg+"]]]"
       res_tok=word_tokenize(res.lower())
       attempts[n] = attempts[n] +1  # matching attempts for n-gram size n
       if len(res_tok) :
          found_tok=subfinder(target_tok,res_tok)
       if found_tok : 
       #   print "( ",seg," : ", res, ")"
       #   print float(len(source_tok))/float((len(source_tok)-n+1))
          if args.counts : 
             successes[n] = successes[n] + len(found_tok)  # successful attempts for n-gram size n
             testhits[n] = testhits[n] + float(len(source_tok))/float((len(source_tok)-n+1)) * len(found_tok)
          else :
             successes[n] = successes[n] + 1  # successful attempts for n-gram size n
             testhits[n] = testhits[n] + float(len(source_tok))/float((len(source_tok)-n+1))
     if args.verbose :
        print "Ngram=", n, " Hits=", testhits[n]

# Compute contribution to MAE using best_a
   prediction=0
   for n in range(0,args.maxngram+1) :
      prediction=prediction+best_a[n]*testhits[n]
   if args.verbose :
      print "Prediction={0} Time={1}".format(prediction, time)
   MAE=MAE+math.fabs(float(time)-prediction)/len(test_data)
# End for train


print "Test set MAE=", MAE
for n in range(1,args.maxngram+1):
   print "Test set", n,"-gram success rate=", float(successes[n])/float(attempts[n])





