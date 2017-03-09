#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
import sys
import pyter
from nltk.tokenize import word_tokenize
import argparse

reload(sys)
sys.setdefaultencoding("utf-8")

parser = argparse.ArgumentParser()

parser.add_argument("hyptextfile",help="Hypothesis sentences")
parser.add_argument("reftextfile",help="Reference sentences")
parser.add_argument("resultfile",help="Result file")
args = parser.parse_args()

reftext=open(args.reftextfile).readlines()
hyptext=open(args.hyptextfile).readlines()

result=open(args.resultfile,"w")

for pair in zip(reftext,hyptext) :
   tokenizedhyp=word_tokenize(pair[0])
   tokenizedref=word_tokenize(pair[1])
   result.write("{0}\n".format(pyter.ter(tokenizedhyp,tokenizedref)*len(tokenizedref)))
