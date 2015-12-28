#! /usr/bin/python3

import dga_features
import sys
import logging

from throttling import lineid, throttler
import vorpalconfig


#pseudo-enum for verdicts
class dubbedNum:
    def __init__(self, value, name):
        self.value = value
        self.name = name

REASONABLE = dubbedNum(0,"REASONBLE")
BORDERLINE = dubbedNum(1,"BORDERLINE")
EXCESSIVE = dubbedNum(2,"EXCESSIVE")

#setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Main")
logger.setLevel(level=vorpalconfig.loggingLevel)
logger.info = throttler(logger.info,3,active=vorpalconfig.throttling)

#Hand-tuned ladders for Decision Tree
pronThresholds = [(1.5,REASONABLE),(1.7,BORDERLINE),(2,EXCESSIVE)]
lexThresholds = [(0.4, REASONABLE),(0.5,BORDERLINE),(0.6,EXCESSIVE)]
sicThresholds = [(3,REASONABLE),(5,BORDERLINE),(10,EXCESSIVE)]

def verdictFromSemiVerdict(v):
    """A 'semiverdict' is a mapping from the feature set to the set {REASONABLE, 
    BORDERLINE, EXCESSIVE}. This function converts a semiverdict to a final 
    verdict on a PCAP."""
    logger.info(
        lineid(),
        "Computing final verdict based on semiverdict:\n\
        \tDomain Collusion: {}\n\
        \tLexical Deviancy: {}\n\
        \tPronouncability Deviancy: {}".format(
            v["Collusions"].name,
            v["Lex. Dev."].name,
            v["Pron. Dev."].name
        )
    )
    result = min(
            v["Collusions"].value,
            max(
                v["Lex. Dev."].value,
                v["Pron. Dev."].value
            )
    )
    return result

def judge(x, ladder):
    """Converts a numeric value to a generic verdict in 
    {REASONABLE, BORDERLINE, EXCESSIVE}, based on a ladder which specifies the 
    relevant thresholds."""
    logger.info(lineid()," Passing judgment on value: {}".format(x))
    ladderReport = ", ".join(["Up to {} is {}".format(j[0],j[1].name) for j in ladder])
    logger.info(lineid(),ladderReport)
    cands = [l for l in ladder if x<=l[0]]
    if cands == []: #The readings are off the scale
        result =  ladder[-1][1] #Return highest value on scale
    else: 
        result = cands[0][1]
    logger.info(lineid()," Value is deemed {}".format(result.name))
    return result


def verdictByFeatures(sic, pron, lex):
    """Takes as input values for a PCAP's domain collusion, pronunciation 
    deviancy and lexical deviancy, and outputs a tuple containing 1. the final 
    verdict in {Clean, Borderline, DGA}, and 2. the original semiverdict."""
    result = {}
    logger.info(
        lineid(),
        "Classifying PCAP based on features:\n\
        \tDomain Collusion: {}\n\
        \tLexical Deviancy: {}\n\
        \tPronouncability Deviancy: {}".format(sic,lex,pron)
    )
    semiVerdict = {
            "Collusions":judge(sic,sicThresholds),
            "Lex. Dev.":judge(lex,lexThresholds),
            "Pron. Dev.":judge(pron,pronThresholds)
    }
    return verdictFromSemiVerdict(semiVerdict), semiVerdict

if __name__ == "__main__":
    logger.info(lineid()," Beginning analysis of traffic sample: {}".format(sys.argv[1]))
    final, semi = verdictByFeatures(*dga_features.fromPcap(sys.argv[1]))
    if final==REASONABLE.value:
        print("Probably not DGA")
    if final==BORDERLINE.value:
        print("Possibly DGA, too close to call")
    if final==EXCESSIVE.value:
        print("Probably DGA")
    
