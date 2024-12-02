#! /usr/bin/env python

'''
    Temporal cliques: Enumerating delta-cliques in temporal graphs. 
    Copyright (C) 2016 Anne-Sophie Himmel

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from CliqueMaster import CliqueMaster
from Neighborhood import Neighborhood
from Clique import Clique
import sys, time
#import optparse
import resource
import csv

import timeit
import argparse
import os

#############################################################################################
# Logger functions  (added by [Boekhout, 2024] for performance logging)
#############################################################################################

class Logger(object):
    def __init__(self, args):
        self.terminal = sys.stdout
        os.makedirs("logfiles-clique-enumeration", exist_ok=True)
        base_name = "logfiles-clique-enumeration/logfile-Himmel-{}_d{}_p{}".format(args["infile"].split("/")[-1],
                                                                               args["delta"], args["pivoting"])
        name_addendum = ".log"
        i = 0
        while os.path.isfile(base_name + name_addendum):
            name_addendum = "-" + str(i) + ".log"
            i += 1
        self.log = open(base_name + name_addendum, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

#############################################################################################
# Input parser class functions  (added by [Boekhout, 2024] for uniform input formatting across algorithms)
#############################################################################################

main_splitter = "================================="

class InputParser(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Enumerate all (delta,gamma)-maximal cliques given a link stream")
        self.setArguments()

    def setArguments(self):
        self.parser.add_argument('-in', "--infile", required=True, help="Location of link stream input file, requiring format '<timestamp> <node_identifier> <node_identifier> <optional weight>'")
        self.parser.add_argument('-out', "--outdir", required=True, help="Location of directory in which output files will be stored for the enumerated delta-gamma-maximal cliques")
        self.parser.add_argument('-l', "--delimiter", default=" ", help="Delimiter used between columns of link stream input file")
        self.parser.add_argument('-d', "--delta", default=1, help="Maximum time period within which there must always be a (weighted) frequency of gamma of each link of a clique to be maximal", type=int)
        self.parser.add_argument('-p', "--pivoting", default=0, type=int,
                      help="Set the algorithm used for pivoting by setting PIVOTING_LVL to one of the following. "
                      "0: Do not use pivoting. "
                      "1: Pick a single arbitrary pivot. "
                      "2: Pick a single pivot maximizing the number of removed elements. "
                      "3: Pick an arbitrary maximal set of pivots. "
                      "4: Pick a set of pivots greedily according to the maximum number of removed elements. "
                      "5: Pick a set of pivots maximizing the number of removed elements.")

    def getInputArgumentsAsDict(self):
        return vars(self.parser.parse_args())

    def printInput(self):
        args = self.getInputArgumentsAsDict()
        print(main_splitter)
        for label in args.keys():
            print("{}: {}".format(self.parser._option_string_actions["--" +label].help, args[label]))
        print(main_splitter + "\n")

#############################################################################################
# Main function(s)
#############################################################################################

def main():
    ##############################################################
    # Added/updated by [Boekhout, 2024] for uniform input formatting across algorithms and performance logging
    ##############################################################
    # Process command line input to obtain input and output base directories
    input_parser = InputParser()
    args = input_parser.getInputArgumentsAsDict()
    sys.stdout = Logger(args)
    input_parser.printInput()

    assert args["delta"] >= 0, "Delta must be positive."
    delta = args["delta"]
    os.makedirs(args["outdir"], exist_ok=True)
    outputfile = os.path.join(args["outdir"], "delta-{}-pivoting-{}.txt".format(args["delta"], args["pivoting"]))
    start_time = timeit.default_timer()
    ##############################################################

    t_min = float('inf')
    t_max = 0
    times = dict()
    vertices = set()

    # Read temporal graph
    with open(args["infile"], 'r') as inf:
        for line in inf:
            contents = line.split()
            t = int(contents[0])
            u = contents[1]
            v = contents[2]

            if u == v:
                print >> sys.stderr, "Ignoring self-loop on vertex " + u + " at time " + str(t)
                continue

            edge = frozenset([u, v])

            # Populate data structures
            if edge not in times: times[edge] = []
            times[edge].append(t)
            if u not in vertices: vertices.add(u)
            if v not in vertices: vertices.add(v)

            t_min = min(t_min, t)
            t_max = max(t_max, t)

    # Start execution
    sys.stdout.write("First Edge: %d \n" % (t_min))
    sys.stdout.write("Last Edge: %d \n" % (t_max))
    sys.stdout.write("# vertices = %d \n" % (len(vertices)))
    amount = 0
    for i in times.keys():
        amount += len(times[i])
    sys.stdout.write("# timestamps = %d \n" % (amount))
    sys.stdout.write("# delta = %d \n " % (delta)) 
    t1 = time.time()
    C = CliqueMaster(times, vertices, t_min-delta, t_max+delta, delta, args["pivoting"])#options.pivoting_lvl)
    t2 = time.time()
    sys.stdout.write("Accumulated time to calculate Cliques: %s seconds \n" % (t2 - t1))
    sys.stdout.write("# maximal Delta-Cliques: %d \n" % (len(C.maxCliques)))
    sys.stdout.write("max Clique Size: %d \n" % (C.maxCliqueSize()))

    ##############################################################
    # Added/updated by [Boekhout, 2024] for post-processing, writing cliques to file, and consistent performance logging
    ##############################################################
    stop_time = timeit.default_timer()
    print("Total runtime (before post processing): {:.2f}s".format(stop_time - start_time))
    print("Resources used (before post processing): {}MB".format(int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)))
    C.postProcess(times)

    with open(outputfile, "w+") as cliquef:
        cliquef.write(str(C) + '\n')

    stop_time = timeit.default_timer()
    print("Total runtime: {:.2f}s".format(stop_time - start_time))
    print("Resources used: {}MB".format(int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)))
    print("Cliques found: {}".format(len(C.maxCliques)))
    ##############################################################

if __name__ == "__main__":
    sys.exit(main())
