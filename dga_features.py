#! /usr/bin/python3

import numpy as np
import os
import pymongo
import collections
import logging


from gutenberg_freqtable import gutenbergFreqtable
import dns_parser
import lexical_rating
from throttling import lineid, throttler
import vorpalconfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Features")
logger.setLevel(level=vorpalconfig.loggingLevel)
logger.info = throttler(logger.info,3,active=vorpalconfig.throttling)

def fromPcap(pcap):
    logger.info(lineid(), " Extracting features from pcap @ {}".format(pcap))
    requests = dns_parser.dnsRequests(pcap)
    if requests == {}:
        logger.info(lineid(), " No DNS Requests; defaulting to all-0 feature values")
        return 0,0,0
    mostCommonResp = collections.Counter(requests.values()).most_common(1)[0][0]
    logger.info(
            lineid(), 
            " Most common DNS Response: {}".format(mostCommonResp)
    )
    relevantDomains = sorted([
        k 
        for k in requests 
        if requests[k]==mostCommonResp
    ])
    logger.info(
            lineid(), 
            " Requests that got this response: {}".format(relevantDomains)
    )
    collusionScore = len(relevantDomains)
    logger.info(
            lineid(), 
            "Maximum domain collusion: {}".format(collusionScore)
    )
    longestRelevantDomains = sorted(relevantDomains, key=len, reverse=True)[:10]
    logger.info(
            lineid(), 
            "Longest 10 relevant requests: {}".format(longestRelevantDomains)
    )
    pronScore = lexScore = 0
    if len(relevantDomains)>0:
        longestRelevantDomains = list(filter(
            lambda x: len(x)>0, 
            longestRelevantDomains
        ))
        if longestRelevantDomains == []: return 0,0,0
        logger.info(lineid(), "Calculating pronunciation deviancy")
        pronScore = np.average(list(map(
            lambda x: gutenbergFreqtable.logProb(x)/(len(x)**2), 
            longestRelevantDomains
        )))
        logger.info(
                lineid(),
                "Final pronunciation deviancy: {}".format(pronScore)
        )
        logger.info(lineid(), "Calculating lexical deviancy")
        lexScore = np.average(list(map(
            lexical_rating.lexicalDeviancy, 
            longestRelevantDomains
        )))
    logger.info(
                lineid(),
                "Final lexical deviancy: {}".format(lexScore)
        )

    return collusionScore, pronScore, lexScore

def recordPcapDirInCollection(directory,collection):
    for dirs, subdirs, files in os.walk(directory):
        for f in files:
            if collection.find_one({"_id":f}): 
                #Do not recalculate features
                continue
            try:
                sic, pron, lex = fromPcap(os.path.join(directory,f))
                result = {
                    "_id":f, 
                    "pronScore":pron, 
                    "lexScore":lex, 
                    "sameIPCount":sic
                }
                collection.insert(result)
            except: pass #TODO: Add saner error handling
