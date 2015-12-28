#! /usr/bin/python3


import itertools
import string
from math import log
import logging

from throttling import lineid, throttler
import vorpalconfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Bigrams")
logger.setLevel(level=vorpalconfig.loggingLevel)
logger.info = throttler(logger.info,3,active=vorpalconfig.throttling)

def ngrams(n=0,alphabet="",word=None):
    if word is not None:
        for i in range(len(word)-n+1):
            gram = word[i:i+n]
            logging.info(gram)
            yield gram 
    else: #generate all ngrams
        for tupl in itertools.product(alphabet,repeat=n): 
            yield "".join([char for char in tupl]) #all possible ngrams

class freqTable:
    def __init__(self, wordlist,n):
        self.frequencies = {}
        self[""] = 0
        self.tableOrder = n
        self.maxWordLen = 0
        self.alphabet = set([])
        for word in wordlist:
            self.maxWordLen = max(self.maxWordLen, len(word))
            for i in range(1,n+1):
                for ngram in ngrams(i,word=word):
                    self.frequencies.setdefault(ngram,0)
                    self[ngram] += 1
                    if (i==1): 
                        self.alphabet |= set([ngram])
                        self[""] += 1


    def __getitem__(self,index): return self.frequencies[index]
    def __setitem__(self,key,value): self.frequencies[key] = value

    def additiveSmooth(self):
        for i in range(1,self.tableOrder+1):
            for k in ngrams(i,alphabet=self.alphabet): 
                self.frequencies.setdefault(k,0)
                self.frequencies[k] += 1
    
    def logProb(self,buf):
        logger.info(lineid()," Calculating surprise bits from input: {}".format(buf))
        result = 0
        for i in range(1,len(buf)+1):
            hist = buf[max(i-self.tableOrder,0):i]
            while len(hist)>0:
                extra = -log(self[hist] / self[hist[:-1]],2)
                result += extra
                logger.info(
                    lineid(),
                    " {} bits of surprise from transition {} => {}".format(
                        extra,
                        hist[:-1],
                        hist
                    )
                )
                hist = hist[1:]
        logger.info(lineid()," Total bits of surprise: {}".format(result))
        logger.info(lineid()," (Normalized: {})".format(result/(len(buf)**2)))
        return result


        
if __name__ == "__main__":
    sft = freqTable(["lorem","ipsum","dolor","sit","amet"],3)
    sft.additiveSmooth()
    print(sft.logProb("loremipsumdolorsitamet"))
