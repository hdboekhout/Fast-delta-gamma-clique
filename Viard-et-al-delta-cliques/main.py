from CliqueMaster import CliqueMaster
from Clique import Clique
import sys

import resource
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
        base_name = "logfiles-clique-enumeration/logfile-Viard-{}_d{}".format(args["infile"].split("/")[-1],
                                                                              args["delta"])
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
        self.parser.add_argument('-d', "--delta", default=1, help="Maximum time period within which there must always be a (weighted) frequency of gamma of each link of a clique to be maximal. (delta = 0, indicates looking for static cliques only)", type=int)

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

if __name__ == "__main__":
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
    output_file = os.path.join(args["outdir"], "delta-{}.txt".format(args["delta"]))
    start_time = timeit.default_timer()
    ##############################################################

    # Initiate
    Cm = CliqueMaster()
    times = dict()
    nodes = dict()
    nb_lines = 0
    resurrect = False

    # Read stream
    #for line in sys.stdin:
    with open(args["infile"], 'r') as inf:
        for line in inf:
            contents = line.split(" ")
            t = int(contents[0])
            u = contents[1].strip()
            v = contents[2].strip()

            link = frozenset([u, v])
            time = (t, t)

            # This a new instance
            Cm.addClique(Clique((link, time), set([])))

            # Populate data structures
            if link not in times:
                times[link] = []
            times[link].append(t)

            if u not in nodes:
                nodes[u] = set()

            if v not in nodes:
                nodes[v] = set()

            nodes[u].add(v)
            nodes[v].add(u)
            nb_lines = nb_lines + 1
    Cm._times = times
    Cm._nodes = nodes
    sys.stderr.write("Processed " + str(nb_lines) + " from stdin\n")

    # Restart execution
    R = Cm.getDeltaCliques(delta)

    ##############################################################
    # Added by [Boekhout, 2024] for post-processing and consistent performance logging
    ##############################################################
    stop_time = timeit.default_timer()
    print("Total runtime (before post processing): {:.2f}s".format(stop_time - start_time))
    print("Resources used (before post processing): {}MB".format(int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)))
    Cm.postProcess()
    sys.stdout.write("# delta = %d\n" % (delta))
    Cm.printCliques(output_file)

    stop_time = timeit.default_timer()
    print("Total runtime: {:.2f}s".format(stop_time - start_time))
    print("Resources used: {}MB".format(int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)))
    print("Cliques found: {}".format(len(Cm._R)))
    ##############################################################
