# Trying to prepare "consensus discount" features
# Using Apertium
# MLF 20170203

# import sys
import subprocess
from nltk.tokenize import word_tokenize
import argparse
import sys


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

# Zip it to loop
training_data=zip(train_pe_time,train_source,train_mt)

languagepair=("en","es")
directory="/home/mlf/apertium-sources/apertium-en-es"

# segment translations will be held in a cache
cache={}


for train in training_data :
   source=train[1]
   target=train[2]
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
   hits=(args.maxngram+1)*[0]
   for n in range(1,args.maxngram+1) :
     hits[n]=0
     for i in range(len(source_tok)-n+1):
       seg=" ".join(source_tok[i:i+n])
       res=cache[seg]
       res_tok=word_tokenize(res.lower())
       if len(res_tok) :
          found_tok=subfinder(target_tok,res_tok)
       if found_tok : 
#          print "( ",seg," : ", res, ")" 
          hits[n] = hits[n] + float(len(source_tok))/float((len(source_tok)-n+1))
     if args.verbose :
        print "Ngram=", n, " Hits=", hits[n]

# End for train







