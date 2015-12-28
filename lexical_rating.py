#! /usr/bin/python3

import numpy as np
import pymongo
from math import log
import random
import string
import itertools
import logging

from gutenberg_freqtable import canonize
import mongoconn
from throttling import lineid, throttler
import vorpalconfig


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Lexical")
logger.setLevel(level=vorpalconfig.loggingLevel)
logger.info = throttler(logger.info,3,active=vorpalconfig.throttling)

def delDictLookup(form):
    result = mongoconn.deletionsDictionary.find_one({"_id":form})
    if result is not None:
        logger.info(lineid(),"DelDict lookup: Form '{}', distance {}".format(
            form,
            result
            )
    )
    else:
        logger.info(
                lineid(),
                "DelDict lookup: Form '{}' not in deletions dictionary".format(
                    form
                )
        )
    if result==None: return result
    return int(result["distance"])

def delDerivs(buf, limit=None):
    if limit==None: limit=len(buf)+1
    result = {}
    for weight in range(limit+1):
        for mod in itertools.combinations(range(len(buf)),weight):
            vector = [1 if j in mod else 0 for j in range(len(buf))] 
            deriv = "".join([char for i,char in enumerate(buf) if vector[i]==0])
            if deriv not in result or result[deriv]>weight: result[deriv]=weight
    logger.info(lineid(),"Deletion derivatives of {}: {}".format(buf,result))
    return result

def lexicalRating(word):
    logger.info(lineid(), "Computing lexical rating of word: {}".format(word))
    if word == "": return 0
    derivs = delDerivs(word,2)
    distances = []
    for form in derivs:
        lookup = delDictLookup(form)
        if lookup is None: continue
        logger.info(
                lineid(),
                "\n\tInput-to-form: {}\n".format(derivs[form])+ 
                "\tForm-to-dictionary: {}\n".format(lookup)+ 
                "\tTotal Distance: {}".format(derivs[form]+lookup)
        )
        distances.append(derivs[form]+lookup)
    if distances==[]: minDistance=len(word)
    else: minDistance = min(distances)
    finalPenalty = 1+minDistance*log(len(word),2)
    logger.info(lineid(),"Final word fragment penalty: {}".format(finalPenalty))
    return finalPenalty

def lexicalDeviancy(buf):
    cur = buf
    result = 0
    while cur:
        step = None
        curRating = None
        for i in range(1,len(cur)+1):
            if step is None or lexicalRating(cur[:i])*step <= curRating*i: 
                step = i
                curRating = lexicalRating(cur[:step])
        logger.info(
                lineid(),
                "Greedy step: Taking away prefix {}".format(cur[:step])
        )
        result += lexicalRating(cur[:step])
        cur = cur[step:]
    result = result/len(buf)
    logger.info(
            lineid(),
            "Final, normalized lexical deviancy for whole input: {}".format(
                result
            )
    )
    return result

    
if __name__=="__main__":
    CORPUS = list(map(canonize, open("/usr/share/dict/words","r").read().splitlines()))
    genGarbage = lambda: "".join([random.choice(string.ascii_lowercase) for i in range(random.choice(range(5,30)))])
    genMeaningful = lambda: "".join([random.choice(CORPUS) for i in range(random.choice(range(1,4)))])
    garbageSet = [genGarbage() for i in range(100)]
    meaningfulSet = [genMeaningful() for i in range(100)]
    garbageDeviancy = list(map(lexicalDeviancy,garbageSet))
    meaningfulDeviancy = list(map(lexicalDeviancy,meaningfulSet))
    print ("Lexical deviancy results")
    print("Garbage set: Average - {}, Std. Dev. - {}".format(np.average(garbageDeviancy),np.std(garbageDeviancy)))
    print("Meaningful set: Average - {}, Std. Dev. - {}".format(np.average(meaningfulDeviancy),np.std(meaningfulDeviancy)))




