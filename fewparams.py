#!/usr/bin/python

import sys
import argparse
import random
import math
import os
import math
import numpy as np
from scipy.optimize import minimize


# Incorporating a better tokenizer which is Unicode-aware
from nltk.tokenize import word_tokenize

reload(sys)
sys.setdefaultencoding("utf-8")


def readdata(filename):
    return ((open(filename).read()).rstrip("\n")).split("\n")


# main


# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("training_time",help="training post-editing time")
parser.add_argument("training_source",help="training source sentence file")
parser.add_argument("training_raw_mt",help="training raw MT sentence file")
parser.add_argument("training_slm",help="training source language model")
parser.add_argument("training_tlm",help="training target language model")

parser.add_argument("test_time",help="test post-editing time")
parser.add_argument("test_source",help="test source sentence file")
parser.add_argument("test_raw_mt",help="test raw MT sentence file")
parser.add_argument("test_slm",help="test source language model")
parser.add_argument("test_tlm",help="test target language model")

parser.add_argument("--select_features", help="Numbers of features to be selected", nargs="+", dest="features")


# Verbose
parser.add_argument("--verbose", action="store_true", dest="verbose", default=False, help="Print each calculation")
# Optimization
parser.add_argument('--maxiter', help="Maximum number of iterations (default 10000)", type=int, default=10000)

args=parser.parse_args()

training_time=readdata(args.training_time)
training_source = readdata(args.training_source)
training_raw_mt = readdata(args.training_raw_mt)
training_slm=readdata(args.training_slm)
training_tlm=readdata(args.training_tlm)

test_time=readdata(args.test_time)
test_source = readdata(args.test_source)
test_raw_mt = readdata(args.test_raw_mt)
test_slm=readdata(args.test_slm)
test_tlm=readdata(args.test_tlm)


training_featureset = [  [ len(q[0]),len(word_tokenize(q[0])),len(q[1]),len(word_tokenize(q[1])), float(q[2]), float(q[3])  ] for q in zip(training_source,training_raw_mt,training_slm,training_tlm) ]
test_featureset = [  [ len(q[0]),len(word_tokenize(q[0])),len(q[1]),len(word_tokenize(q[1])), float(q[2]), float(q[3])  ] for q in zip(test_source,test_raw_mt,test_slm,test_tlm) ]


training_nexamples=len(zip(training_featureset,training_time))
test_nexamples=len(zip(test_featureset,training_time))

# total 6 features
ntotalfeatures=6

# selected features:
selected=args.features
nfeatures=len(selected)


# Initialize parameter vector

# a0=np.array([0 for y in range(nfeatures)])
a0=np.array([np.random.randn() for y in range(nfeatures)])
def mae(a) :
   MAE=0
   for m in range(nexamples) :
      dev=float(time[m])
      for f in range(nfeatures) :
         dev=dev-a[f]*featureset[m][int(selected[f])]
      MAE=MAE+math.fabs(dev)
   return MAE/nexamples

# Training set data
featureset=training_featureset
time=training_time
nexamples=training_nexamples

# Optimize to an error of 0.0001 in MAE (will change later, can also use BFGS)
result = minimize(mae, a0, method='nelder-mead', options={'fatol' : 1e-6, 'disp' : True, 'maxiter' : args.maxiter})

if result.success :
   print "Optimization successful in {0} iterations".format(result.nit) 
else : 
   print "Optimization unsuccessful"
   print result.status

print "Result=", result.x
print "Coefficients"

featurenames=["Source char=", "Source word=", "MT char=", "MT word=", "SLM=", "TLM="]
for j,f in enumerate(selected):
   print featurenames[int(f)], (result.x)[j]

print "Training set MAE=", mae(result.x)

print "Results on testset"

# Test set data
featureset=test_featureset
time=test_time
nexamples=test_nexamples

print "Test set MAE=", mae(result.x)

