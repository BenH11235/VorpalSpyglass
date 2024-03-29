Contributed By Check Point Software Technologies LTD. As seen at 32C3.

# Vorpal Spyglass

tl;dr: Vorpal Spyglass is a tool for automatic detection of autogenerated domains in PCAP-format traffic captures. It takes the path to a PCAP as input and outputs a result: "Probably DGA", "Borderline" or "Probably clean".

DGAs are used by malware as a fallback mechanism in case communication with the campaign's C&C server is cut at the DNS level. To operate, they rely on a pseudorandom generator which takes as input a public seed relevant to that day (e.g. the date) and produce, as output, a large number of domain names. At the beginning of each day, campaign management at the server side chooses a domain from today's list at random, and registers it to point at the C&C server's IP address. When an infected machine attempts to contact the C&C server, it will retrieve today's domain list and make DNS queries for every single domain in turn, until it gets a positive response and the C&C server's IP address.

This setup makes preventing malware from communicating with its C&C server more difficult. The domain names being used are transient. Without access to the specific DGA implementation being used, chasing down and blocking the domains pre-emptively is not possible. And access to the specific DGA implementation will not come easily - the effort will require a qualified reverse enginneer, not to mention knowledge and possession of the relevant executable in the first place.

For this reason, it is worthwhile to detect DGA traffic automatically. Instead of taking shots in the dark, the journey of shutting down the DGA infrastructure can begin with a helpful pointing finger towards the culprit sample. Further, automatic detection can also lead to blocking the DGA traffic right there and then - though this introduces issues of performance, and generally the implementation here was not geared toward this use case. Finally, automatic detection of DGA can serve to determine a single feature as a part of a wider-scale automatic analysis effort.

Vorpal Spyglass relies on three features in order to attempt classification of traffic as either contaminated with, or clean of, DGA:
* The maximum number of DNS requests that mapped to the same result (either an IP address or an NXDOMAIN)
* Among the longest 10 of the request domains: Average bigram inverse-log-probability
* Among the longest 10 of the request domains: Average approximation of distance from domain name to concatenation of dictionary words

Experimentally, different classifiers based on these features have produced different results. So far, the best results seem to follow from using a decision tree algorithm with hand-tuned parameters based on human analysis of Training PCAPs.

## Installation

Vorpal Spyglass requires the following to operate:
* [Python3](http://python.org)
* [numpy](http://numpy.org)
* [pyshark](https://github.com/KimiNewt/pyshark) (Requires a working installation of [tshark](https://www.wireshark.org/docs/wsug_html_chunked/AppToolstshark.html))
* [pymongo](https://api.mongodb.org/python/current/) (Requires a working installation of [mongodb](https://www.mongodb.org/))

Clone the repository to your local directory of choice by running git from the command line:

`git clone https://github.com/BenH11235/VorpalSpyglass`

Alternately, download a zip of the source code via HTTP: click [here](https://github.com/BenH11235/VorpalSpyglass/archive/master.zip)

Make sure that the server address and port in vorpalconfig.py are correct for your instance of mongodb. 

Run populate_del_dict.py and wait 24 hours for the dictionary to be populated (yes, seriously). We toyed a few times with an alternate approach that would cut down the generation time by using a tweaked variation of a Bloom filter, but ultimately were not able to get a PoC to work. 

## Usage

From the command line, execute:

`path-to-python classifyPcap.py inputFilePath`

path-to-python should be replaced with the path to your Python 3 interpreter executable. On linux and OSX you can run "which python" to find out where this is. On Windows environments, the default location is C:\PythonXX\python.exe where XX are digits representing your version number (e.g. Python34 for Python 3.4). inputFilePath should be replaced with the path to a file containing the input pcap.

## History

2015-12-28, v0.1: First upload of Vorpal Spyglass

