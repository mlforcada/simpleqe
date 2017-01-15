#!/usr/bin/python

# Mikel L Forcada 2017
# 
# Weighted distance-based quality (postediting time) estimation
# The programme reads three training files and three testing files
# Three files: (1) time measurement, (2) source segment, (3) MTed segment
# The program computes average times per source character, per source 
# word, per machine translated characters and per machine translated word, 
# and computes the error over the source text.
# and beta).


import sys
import argparse
import random
import math

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
parser.add_argument("--verbose", action="store_true", dest="verbose", default=False, help="Print each calculation")
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


for test in test_zipped :

   t_char_source=a_char_source*test[1]
   t_word_source=a_word_source*test[2]
   t_char_mt=a_char_mt*test[3]
   t_word_mt=a_word_mt*test[4]

   MAE_char_source = MAE_char_source+math.fabs(test[0]-t_char_source)
   MAE_word_source = MAE_word_source+math.fabs(test[0]-t_word_source)
   MAE_char_mt     = MAE_char_mt    +math.fabs(test[0]-t_char_mt)
   MAE_word_mt     = MAE_word_mt    +math.fabs(test[0]-t_word_mt)

   RMSE_char_source = RMSE_char_source+(test[0]-t_char_source)*(test[0]-t_char_source)
   RMSE_word_source = RMSE_word_source+(test[0]-t_word_source)*(test[0]-t_word_source)
   RMSE_char_mt     = RMSE_char_mt    +(test[0]-t_char_mt)*(test[0]-t_char_mt)
   RMSE_word_mt     = RMSE_word_mt    +(test[0]-t_word_mt)*(test[0]-t_word_mt)

n=len(test_zipped)
print "MAE, char, source =", MAE_char_source/n
print "MAE, word, source =", MAE_word_source/n
print "MAE, char, mt =", MAE_char_mt/n
print "MAE, word, mt =", MAE_word_mt/n
print "RMSE, char, source =", math.sqrt(RMSE_char_source/n)
print "RMSE, word, source =", math.sqrt(RMSE_word_source/n)
print "RMSE, char, mt =", math.sqrt(RMSE_char_mt/n)
print "RMSE, word, mt =", math.sqrt(RMSE_word_mt/n)


