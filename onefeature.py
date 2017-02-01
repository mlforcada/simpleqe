#!/usr/bin/python

# Mikel L Forcada 2017
# 
# Single feature, MAE-minimized, quality estimation and testing

import sys
import argparse
import math

reload(sys)
sys.setdefaultencoding("utf-8")

def readdata(filename):
    return ((open(filename).read()).rstrip("\n")).split("\n")

# main

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("training_set",help="Training set")
parser.add_argument("test_set",help="Test set")
parser.add_argument("--mae_search", nargs=3, dest="mae_search", help="Lowest, Highest, Number of points")
parser.add_argument("--verbose", action="store_true", dest="verbose", default=False, help="Print each calculation")
args=parser.parse_args()

# read parameters
if args.mae_search :
     loval=float(args.mae_search[0])
     hival=float(args.mae_search[1])
     npoints = int(args.mae_search[2])

# read files
training_data = readdata(args.training_set)
test_data = readdata(args.test_set)

train_f = [t.split()[0] for t in training_data]
train_t = [t.split()[1] for t in training_data]
test_f = [t.split()[0] for t in test_data]
test_t = [t.split()[1] for t in test_data]

bestMAE=float("inf")
besta = loval
ntrain=len(train_f)
for i in range(npoints+1) :
   a = loval + i*(hival-loval)/npoints
   MAE=0
   for pair in zip(train_f,train_t) :
       MAE = MAE + math.fabs(float(pair[1])-a*(float(pair[0])))/ntrain
   if MAE<bestMAE :
      bestMAE=MAE
      besta=a
     
print "Best a=", besta
print "Best training-set MAE=", bestMAE

MAE=0
ntest=len(test_f)
for pair in zip(test_f,test_t) : 
   MAE = MAE + math.fabs(float(pair[1])-besta*(float(pair[0])))/ntest

print "Testset MAE=", MAE


