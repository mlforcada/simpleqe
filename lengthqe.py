#!/usr/bin/python

# Mikel L Forcada 2017
# 
# Weighted distance-based quality (postediting time) estimation
# The programme reads three training files and three testing files
# Three files: (1) time measurement, (2) source segment, (3) MTed segment
# The program computes average times per source character, per source 
# word, per machine translated characters and per machine translated word, 
# and computes the MAE and RMSE errors over the test corpus.

import sys
import argparse
import random
import math
import os

# Incorporating a better tokenizer which is Unicode-aware
from nltk.tokenize import word_tokenize

reload(sys)
sys.setdefaultencoding("utf-8")


def readdata(filename):
    return ((open(filename).read()).rstrip("\n")).split("\n")


# main


# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("tr_time",help="Training PE time")
parser.add_argument("tr_source", help="Training source segments")
parser.add_argument("tr_mt", help="Training MTed segments")
parser.add_argument("te_time",help="Testing PE time")
parser.add_argument("te_source", help="Testing source segments")
parser.add_argument("te_mt", help="Testing MTed segments")
parser.add_argument("--mae_search", nargs=3, dest="mae_search", help="Lowest, Highest, Number of points")
parser.add_argument("--verbose", action="store_true", dest="verbose", default=False, help="Print each calculation")
parser.add_argument("--produce_output", nargs=1, dest="fileprefix", help="Produce output for MAE-optimized")
args=parser.parse_args()



train_pe_time = readdata(args.tr_time)
train_source = readdata(args.tr_source)
train_mt = readdata(args.tr_mt)
test_pe_time = readdata(args.te_time)
test_source = readdata(args.te_source)
test_mt = readdata(args.te_mt)


# Tokenize as the input is zipped (using lambda (!))
# This could be written more nicely I assume
# idea taken from http://stackoverflow.com/questions/8372399/zip-with-list-output-instead-of-tuple
postzip = lambda a,b,c : [ [ float(q[0]), len(q[1]), len(word_tokenize(q[1])), len(q[2]), len(word_tokenize(q[2])) ] for q in zip(a,b,c) ]


# Lengths computed while zipping.
train_zipped=postzip(train_pe_time,train_source,train_mt)  # 0 is time, 1 is source, 2 is mt
test_zipped=postzip(test_pe_time,test_source,test_mt)

sxy_char_source =0
sxy_word_source =0
sxx_char_source =0
sxx_word_source =0
sxy_char_mt =0
sxy_word_mt =0
sxx_char_mt =0
sxx_word_mt =0

for train in train_zipped :
#    print train[0],train[1],train[2], train[3], train[4] 
    sxx_char_source = train[1]*train[1]
    sxy_char_source = train[0]*train[1]
    sxx_word_source = train[2]*train[2]
    sxy_word_source = train[0]*train[2]
    sxx_char_mt = train[3]*train[3]
    sxy_char_mt = train[0]*train[3]
    sxx_word_mt = train[4]*train[4]
    sxy_word_mt = train[0]*train[4]

# linear regression time = a * length

a_char_source = sxy_char_source/sxx_char_source
a_char_mt = sxy_char_mt/sxx_char_mt
a_word_source = sxy_word_source/sxx_word_source
a_word_mt = sxy_word_mt / sxx_word_mt

MAE_char_source=0
MAE_word_source=0
MAE_char_mt=0
MAE_word_mt=0
RMSE_char_source=0
RMSE_word_source=0
RMSE_char_mt=0
RMSE_word_mt=0


for train in train_zipped :  # get best RMSE over training set

   t_char_source=a_char_source*train[1]
   t_word_source=a_word_source*train[2]
   t_char_mt=a_char_mt*train[3]
   t_word_mt=a_word_mt*train[4]

   MAE_char_source = MAE_char_source+math.fabs(train[0]-t_char_source)
   MAE_word_source = MAE_word_source+math.fabs(train[0]-t_word_source)
   MAE_char_mt     = MAE_char_mt    +math.fabs(train[0]-t_char_mt)
   MAE_word_mt     = MAE_word_mt    +math.fabs(train[0]-t_word_mt)

   RMSE_char_source = RMSE_char_source+(train[0]-t_char_source)*(train[0]-t_char_source)
   RMSE_word_source = RMSE_word_source+(train[0]-t_word_source)*(train[0]-t_word_source)
   RMSE_char_mt     = RMSE_char_mt    +(train[0]-t_char_mt)*(train[0]-t_char_mt)
   RMSE_word_mt     = RMSE_word_mt    +(train[0]-t_word_mt)*(train[0]-t_word_mt)

ntrain=len(train_zipped) 

if args.verbose :
   print "RMSE-optimized values (over training set):"
   print "RMSE, char, source =", math.sqrt(RMSE_char_source/ntrain), " ; rate=", a_char_source, " s/char"
   print "RMSE, word, source =", math.sqrt(RMSE_word_source/ntrain), " ; rate=", a_word_source, " s/word"
   print "RMSE, char, mt     =", math.sqrt(RMSE_char_mt/ntrain),     " ; rate=", a_char_mt,     " s/char"
   print "RMSE, word, mt     =", math.sqrt(RMSE_word_mt/ntrain),     " ; rate=", a_word_mt,     " s/word"


# print "RMSE-optimized MAE values (over training set, suboptimal):"
# print "MAE, char, source =", MAE_char_source/ntrain,            " ; rate=", a_char_source, " s/char"
# print "MAE, word, source =", MAE_word_source/ntrain,            " ; rate=", a_word_source, " s/word"
# print "MAE, char, mt     =", MAE_char_mt/ntrain,                " ; rate=", a_char_mt,     " s/char"
# print "MAE, word, mt     =", MAE_word_mt/ntrain,                " ; rate=", a_word_mt,     " s/word"



if args.mae_search :
     lorel=float(args.mae_search[0])
     hirel=float(args.mae_search[1])
     npoints = int(args.mae_search[2])

     best_a_char_source=-1
     best_a_word_source=-1 
     best_a_char_mt    =-1
     best_a_word_mt    =-1
 
     best_MAE_char_source=float("inf")
     best_MAE_word_source=float("inf")
     best_MAE_char_mt=float("inf")
     best_MAE_word_mt=float("inf")

     lo_a_char_source=a_char_source*lorel
     lo_a_word_source=a_word_source*lorel
     lo_a_char_mt    =a_char_mt    *lorel
     lo_a_word_mt    =a_word_mt    *lorel

     hi_a_char_source=a_char_source*hirel
     hi_a_word_source=a_word_source*hirel
     hi_a_char_mt    =a_char_mt    *hirel
     hi_a_word_mt    =a_word_mt    *hirel
 
     step_a_char_source=(hi_a_char_source-lo_a_char_source)/npoints
     step_a_word_source=(hi_a_word_source-lo_a_word_source)/npoints
     step_a_char_mt    =(hi_a_char_mt    -lo_a_char_mt)/npoints
     step_a_word_mt    =(hi_a_word_mt    -lo_a_word_mt)/npoints


     for i in range(npoints+1) :	
        cur_a_char_source=lo_a_char_source+i*step_a_char_source
        cur_a_word_source=lo_a_word_source+i*step_a_word_source
        cur_a_char_mt    =lo_a_char_mt    +i*step_a_char_mt
        cur_a_word_mt    =lo_a_word_mt    +i*step_a_word_mt

        MAE_char_source=0
        MAE_word_source=0
        MAE_char_mt=0
        MAE_word_mt=0

        
        for train in train_zipped :
  
           t_char_source=cur_a_char_source*train[1]
           t_word_source=cur_a_word_source*train[2]
           t_char_mt=cur_a_char_mt*train[3]
           t_word_mt=cur_a_word_mt*train[4]

           MAE_char_source = MAE_char_source+math.fabs(train[0]-t_char_source)
           MAE_word_source = MAE_word_source+math.fabs(train[0]-t_word_source)
           MAE_char_mt     = MAE_char_mt    +math.fabs(train[0]-t_char_mt)
           MAE_word_mt     = MAE_word_mt    +math.fabs(train[0]-t_word_mt)
 
        #endfor
        if MAE_char_source/ntrain < best_MAE_char_source :
           best_MAE_char_source = MAE_char_source/ntrain
           best_a_char_source=cur_a_char_source
        if MAE_word_source/ntrain < best_MAE_word_source :
           best_MAE_word_source = MAE_word_source/ntrain
           best_a_word_source = cur_a_word_source
        if MAE_char_mt    /ntrain < best_MAE_char_mt     :
           best_MAE_char_mt     = MAE_char_mt    /ntrain
           best_a_char_mt     = cur_a_char_mt
        if MAE_word_mt    /ntrain < best_MAE_word_mt     :
           best_MAE_word_mt     = MAE_word_mt    /ntrain
           best_a_word_mt     = cur_a_word_mt

     if args.verbose :
        print "MAE-optimized MAE values (over training set):"
        print "MAE, char, source =", best_MAE_char_source,            " ; rate=", best_a_char_source, " s/char"
        print "MAE, word, source =", best_MAE_word_source,            " ; rate=", best_a_word_source, " s/word"
        print "MAE, char, mt     =", best_MAE_char_mt,                " ; rate=", best_a_char_mt,     " s/char"
        print "MAE, word, mt     =", best_MAE_word_mt,                " ; rate=", best_a_word_mt,     " s/word"
             

# Now test!!

MAEopt_MAE_char_source=0
MAEopt_MAE_word_source=0
MAEopt_MAE_char_mt=0
MAEopt_MAE_word_mt=0
RMSEopt_MAE_char_source=0
RMSEopt_MAE_word_source=0
RMSEopt_MAE_char_mt=0
RMSEopt_MAE_word_mt=0
MAEopt_RMSE_char_source=0
MAEopt_RMSE_word_source=0
MAEopt_RMSE_char_mt=0
MAEopt_RMSE_word_mt=0
RMSEopt_RMSE_char_source=0
RMSEopt_RMSE_word_source=0
RMSEopt_RMSE_char_mt=0
RMSEopt_RMSE_word_mt=0


if args.fileprefix :
   out_char_source=open(args.fileprefix[0]+"_char_source.result", "w")
   out_word_source=open(args.fileprefix[0]+"_word_source.result", "w")
   out_char_mt=open(args.fileprefix[0]+"_char_mt.result", "w")
   out_word_mt=open(args.fileprefix[0]+"_word_mt.result", "w")

ntest=len(test_zipped)
counter=0
for test in test_zipped :
 
   counter=counter+1

   t_char_source=a_char_source*test[1]
   t_word_source=a_word_source*test[2]
   t_char_mt=a_char_mt*test[3]
   t_word_mt=a_word_mt*test[4]


   MAEopt_MAE_char_source = MAEopt_MAE_char_source+math.fabs(test[0]-best_a_char_source*test[1])
   MAEopt_MAE_word_source = MAEopt_MAE_word_source+math.fabs(test[0]-best_a_word_source*test[2])
   MAEopt_MAE_char_mt     = MAEopt_MAE_char_mt    +math.fabs(test[0]-best_a_char_mt*test[3])
   MAEopt_MAE_word_mt     = MAEopt_MAE_word_mt    +math.fabs(test[0]-best_a_word_mt*test[4])


   if args.fileprefix : 
       
      out_char_source.write("AlaShefLen_char_source+\t{0}\t{1}".format(counter,best_a_char_source*test[1])+os.linesep)
      out_word_source.write("AlaShefLen_word_source\t{0}\t{1}".format(counter,best_a_word_source*test[2])+os.linesep)
      out_char_mt.write("AlaShefLen_char_mt\t{0}\t{1}".format(counter,best_a_char_mt*test[3])+os.linesep)
      out_word_mt.write("AlaShefLen_word_mt\t{0}\t{1}".format(counter,best_a_word_mt*test[4])+os.linesep)   


   MAEopt_RMSE_char_source = MAEopt_RMSE_char_source+(test[0]-best_a_char_source*test[1])*(test[0]-best_a_char_source*test[1])
   MAEopt_RMSE_word_source = MAEopt_RMSE_word_source+(test[0]-best_a_word_source*test[2])*(test[0]-best_a_word_source*test[2])
   MAEopt_RMSE_char_mt     = MAEopt_RMSE_char_mt    +(test[0]-best_a_char_mt*test[3])*(test[0]-best_a_char_mt*test[3])
   MAEopt_RMSE_word_mt     = MAEopt_RMSE_word_mt    +(test[0]-best_a_word_mt*test[4])*(test[0]-best_a_word_mt*test[4])

   RMSEopt_MAE_char_source = RMSEopt_MAE_char_source+math.fabs(test[0]-t_char_source)
   RMSEopt_MAE_word_source = RMSEopt_MAE_word_source+math.fabs(test[0]-t_word_source)
   RMSEopt_MAE_char_mt     = RMSEopt_MAE_char_mt    +math.fabs(test[0]-t_char_mt)
   RMSEopt_MAE_word_mt     = RMSEopt_MAE_word_mt    +math.fabs(test[0]-t_word_mt)

   RMSEopt_RMSE_char_source = RMSEopt_RMSE_char_source+(test[0]-a_char_source*test[1])*(test[0]-a_char_source*test[1])
   RMSEopt_RMSE_word_source = RMSEopt_RMSE_word_source+(test[0]-a_word_source*test[2])*(test[0]-a_word_source*test[2])
   RMSEopt_RMSE_char_mt     = RMSEopt_RMSE_char_mt    +(test[0]-a_char_mt*test[3])*(test[0]-a_char_mt*test[3])
   RMSEopt_RMSE_word_mt     = RMSEopt_RMSE_word_mt    +(test[0]-a_word_mt*test[4])*(test[0]-a_word_mt*test[4])

# end for test in test_zipped

print "-------------"
print "RMSE for RMSE-optimized values (over test set):"
print "RMSE, char, source =", math.sqrt(RMSEopt_RMSE_char_source/ntest), " ; rate=", a_char_source, " s/char"
print "RMSE, word, source =", math.sqrt(RMSEopt_RMSE_word_source/ntest), " ; rate=", a_word_source, " s/word"
print "RMSE, char, mt     =", math.sqrt(RMSEopt_RMSE_char_mt/ntest),     " ; rate=", a_char_mt,     " s/char"
print "RMSE, word, mt     =", math.sqrt(RMSEopt_RMSE_word_mt/ntest),     " ; rate=", a_word_mt,     " s/word"
print "-------------"
print "RMSE for MAE-optimized values (over test set):"
print "RMSE, char, source =", math.sqrt(MAEopt_RMSE_char_source/ntest), " ; rate=", best_a_char_source, " s/char"
print "RMSE, word, source =", math.sqrt(MAEopt_RMSE_word_source/ntest), " ; rate=", best_a_word_source, " s/word"
print "RMSE, char, mt     =", math.sqrt(MAEopt_RMSE_char_mt/ntest),     " ; rate=", best_a_char_mt,     " s/char"
print "RMSE, word, mt     =", math.sqrt(MAEopt_RMSE_word_mt/ntest),     " ; rate=", best_a_word_mt,     " s/word"
print "-------------"
print "MAE for RMSE-optimized MAE values (over test set):"
print "MAE, char, source =", RMSEopt_MAE_char_source/ntest,            " ; rate=", a_char_source, " s/char"
print "MAE, word, source =", RMSEopt_MAE_word_source/ntest,            " ; rate=", a_word_source, " s/word"
print "MAE, char, mt     =", RMSEopt_MAE_char_mt/ntest,                " ; rate=", a_char_mt,     " s/char"
print "MAE, word, mt     =", RMSEopt_MAE_word_mt/ntest,                " ; rate=", a_word_mt,     " s/word"
print "-------------"
print "MAE for MAE-optimized MAE values (over test set):"
print "MAE, char, source =", MAEopt_MAE_char_source/ntest,            " ; rate=", best_a_char_source, " s/char"
print "MAE, word, source =", MAEopt_MAE_word_source/ntest,            " ; rate=", best_a_word_source, " s/word"
print "MAE, char, mt     =", MAEopt_MAE_char_mt/ntest,                " ; rate=", best_a_char_mt,     " s/char"
print "MAE, word, mt     =", MAEopt_MAE_word_mt/ntest,                " ; rate=", best_a_word_mt,     " s/word"

if args.fileprefix :
   out_char_source.close()
   out_word_source.close()
   out_char_mt.close()
   out_word_mt.close()

         


     

