#! /usr/bin/python3
import os
import pyshark
from gutenberg_freqtable import canonize
from collections import Counter

IS_RESPONSE = '1'
RTYPE_A = '0x0001'
RTYPE_AAAA = '0x001c'
RCODE_NXDOMAIN = '3'
MAX_PACKETS_READ = 400

def dnsRequests(pcap):
    pkts = pyshark.FileCapture(pcap)
    queries = {}
    result = {}
    pkts_read = 0
    for pkt in pkts:
        pkts_read += 1
        if pkts_read >= MAX_PACKETS_READ: break
        try:    
            if pkt.dns.qry_type not in [RTYPE_A,RTYPE_AAAA]: continue
            if pkt.dns.flags_rcode==RCODE_NXDOMAIN:
                reply = "NXDOMAIN"
            else:
                reply = pkt.dns.resp_addr
            name = pkt.dns.qry_name
            queries[name] = reply
        except AttributeError: pass

    #Extract the "most unique level domain" from each query
    freqs = Counter([
        level 
        for item in queries.keys() 
        for level in item.split(".")
    ])
    for query in queries:
        cands = query.split(".")
        maxinf = min(cands, key=freqs.get)
        result[canonize(maxinf)] = queries[query]
    return result


