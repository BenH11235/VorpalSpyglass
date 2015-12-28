#!/usr/bin/python3

from mongoconn import deletionsDictionary
from lexical_rating import delDerivs, delDictLookup
from gutenberg_freqtable import canonize
import vorpalconfig


print("Deletions dictionary builder started.")
print("Go do something productive with your life now.")
print("This is going to take a while.")
with open(vorpalconfig.dictionaryLocation,"r") as fh:
    for word in fh.read().split('\n'):
        for deriv in delDerivs(canonize(word)).items():
            stem, dist = deriv
            result = delDictLookup(stem)
            if result is None or result>dist:
                deletionsDictionary.update(
                        {"_id":stem},
                        {"$set":{"distance":dist}},
                        upsert=True
                )


