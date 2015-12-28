#! /usr/bin/python3

import entropylib
import string
import nltk
import pickle

FT_FNAME = "gutenberg_freqtable.dat"
CORPUS = nltk.corpus.gutenberg
TABLE_ORDER = 2
canonize = lambda txt: "".join([t.lower() for t in txt if t in string.ascii_letters])
def canonizedCorpus():
	return [canonize(word) for word in CORPUS.words() if canonize(word)!=""]


#if freqtable does not exist, create it
try: 
	fh = open(FT_FNAME,"rb")
	fh.close()
except:
	print("Building freqtable")
	import os
	gutenbergFreqtable = entropylib.freqTable(canonizedCorpus(),TABLE_ORDER)
	gutenbergFreqtable.additiveSmooth()
	
	with open(FT_FNAME,'wb') as fh:
		pickle.dump(gutenbergFreqtable,fh)

with open(FT_FNAME,"rb") as fh:
	gutenbergFreqtable = pickle.load(fh)


