#!/usr/bin/python

# Mikel L Forcada 2017
# 
# Weighted distance-based quality (postediting time) estimation
# The programme reads three training files and three testing files
# Three files: (1) time measurement, (2) source segment, (3) MTed segment
# The program performs a grid search in parameter space (2 parameters: alpha 
# and beta).

# To do (20170110)
# Look for ways to avoid expensive mpmath computation of exponentials
# Allow to optimize just alpha or just beta


import sys
import argparse
# from functools import wraps
import math
import random
import mpmath # to avoid underflows in exponentials

# Incorporating a better tokenizer which is Unicode-aware
from nltk.tokenize import word_tokenize

reload(sys)
sys.setdefaultencoding("utf-8")


def readdata(filename):
    return ((open(filename).read()).rstrip("\n")).split("\n")


# Levenshtein distance between two sequences, taken from 
# https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python

def levenshtein(seq1, seq2):
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
    return thisrow[len(seq2) - 1]


# main


# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("tr_time",help="Training PE time")
parser.add_argument("tr_source", help="Training source segments")
parser.add_argument("tr_mt", help="Training MTed segments")
parser.add_argument("te_time",help="Testing PE time")
parser.add_argument("te_source", help="Testing source segments")
parser.add_argument("te_mt", help="Testing MTed segments")
parser.add_argument("low_alpha", type=float, help="Low value of alpha")
parser.add_argument("high_alpha", type=float, help="High value of alpha")
parser.add_argument("low_beta", type=float, help="Low value of beta")
parser.add_argument("high_beta", type=float, help="High value of beta")
parser.add_argument("npoints", type=int, help="Number of points")
parser.add_argument("--tokenize", action="store_true", dest="tokenize", help="Use advanced tokenization (default: word and space-based)")
parser.add_argument("--character", action="store_true", dest="character", help="Use character-based edit distance (default: word-based")
parser.add_argument("--mae", action="store_true", dest="mae", default=False, help="Minimize according to MAE (default RMSE)")
args=parser.parse_args()


train_pe_time = readdata(args.tr_time)
train_source = readdata(args.tr_source)
train_mt = readdata(args.tr_mt)
test_pe_time = readdata(args.te_time)
test_source = readdata(args.te_source)
test_mt = readdata(args.te_mt)
alpha1 = args.low_alpha
alpha2 = args.high_alpha
beta1 = args.low_beta
beta2 = args.high_beta
points = args.npoints


# Tokenize as the input is zipped (using lambda (!))
# This could be written more nicely I assume
# idea taken from http://stackoverflow.com/questions/8372399/zip-with-list-output-instead-of-tuple
if args.tokenize :
   postzip = lambda a,b,c : [ [ q[0], word_tokenize(q[1]), word_tokenize(q[2]) ] for q in zip(a,b,c) ]
elif args.character :
   postzip = lambda a,b,c : [ [ q[0], q[1], q[2] ] for q in zip(a,b,c) ]
else : # poor man's tokenization
   postzip = lambda a,b,c : [ [ q[0], q[1].split() , q[2].split ] for q in zip(a,b,c) ]

# Input is tokenized before zipping.
train_zipped=postzip(train_pe_time,train_source,train_mt)  # 0 is time, 1 is source, 2 is mt
test_zipped=postzip(test_pe_time,test_source,test_mt)
# print len(test_zipped)

dscache=[]   # rudimentary cache for ds and dmt below
dmtcache=[]
for i in range(len(train_zipped)*len(test_zipped)) :
    dscache.append(-1)
    dmtcache.append(-1)

bestalpha=alpha1
bestbeta=beta1
besterr=float("inf")

for ia in range(0,points+1) :
  for ib in range(0,points+1) :
    i=0; # cache index
    currentalpha = alpha1 + (alpha2-alpha1)*ia/points
    currentbeta = beta1 + (beta2-beta1)*ib/points
    forRMSE=0
    forMAE=0
    test_samples=0
    for test in test_zipped :
        numerator=0
        denominator=0
        for train in train_zipped :
	   if dscache[i]==-1 :
                ds=levenshtein(test[1],train[1])
                dscache[i]=ds
                dmt=levenshtein(test[2],train[2])
                dmtcache[i]=dmt
           else :
                ds=dscache[i]
                dmt=dmtcache[i]
           exponent=-currentalpha*ds-currentbeta*dmt
           if math.fabs(exponent) > 700 : # +709.7827 or -745.133 for regular floats 
              factor=mpmath.exp(exponent)
           else:
              factor=math.exp(exponent)
           numerator = numerator + factor*float(train[0])
           denominator = denominator + factor
           i = i + 1 # next train--test pair in cache
#        print denominator
        predicted_time = numerator / denominator
        test_samples = test_samples + 1
        dev=predicted_time-float(test[0])
        forRMSE = forRMSE + dev*dev
        forMAE = forMAE + math.fabs(dev)
#        print predicted_time,float(test[0])
    RMSE = math.sqrt(forRMSE/test_samples)
    MAE = forMAE/test_samples
#    print currentalpha, currentbeta, err
    if args.mae : 
         err=MAE
    else :
         err=RMSE
    if err < besterr :
         besterr = err
         bestalpha = currentalpha
         bestbeta = currentbeta
 
         print bestalpha, bestbeta, "RMSE=", RMSE, "MAE=", MAE
    
print "Best of", test_samples, ":"
print bestalpha, bestbeta, besterr            

