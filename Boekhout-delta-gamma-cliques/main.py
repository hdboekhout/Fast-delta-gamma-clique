"""
MIT License

Copyright (c) 2024 Hanjo Boekhout

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
"""

from CliqueMaster import CliqueMaster

import resource
import timeit
import argparse
import sys
import os

main_splitter = "================================="

#############################################################################################
# Logger functions
#############################################################################################

class Logger(object):
  def __init__(self, args):
    self.terminal = sys.stdout
    #self.log = open("logfile-simple-core-team-identification.log", "w")
    os.makedirs("logfiles-clique-enumeration", exist_ok=True)
    if args["weighted"]:
      base_name = "logfiles-clique-enumeration/logfile-Boekhout-BSF-{}_d{}_g{}_weighted".format(args["infile"].split("/")[-1], args["delta"], args["gamma"])
    else:
      base_name = "logfiles-clique-enumeration/logfile-Boekhout-BSF-{}_d{}_g{}".format(args["infile"].split("/")[-1], args["delta"], args["gamma"])
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
# Input parser class functions
#############################################################################################

class InputParser(object):
  def __init__(self):
    self.parser = argparse.ArgumentParser(description="Enumerate all (delta,gamma)-maximal cliques given a link stream")
    self.setArguments()

  def setArguments(self):
    self.parser.add_argument('-in', "--infile", required=True, help="Location of link stream input file, requiring format '<timestamp> <node_identifier> <node_identifier> <optional weight>'")
    self.parser.add_argument('-out', "--outdir", required=True, help="Location of directory in which output files will be stored for the enumerated delta-gamma-maximal cliques")
    self.parser.add_argument('-l', "--delimiter", default=" ", help="Delimiter used between columns of link stream input file")
    self.parser.add_argument('-d', "--delta", default=1, help="Maximum time period within which there must always be a (weighted) frequency of gamma of each link of a clique to be maximal", type=int)
    self.parser.add_argument('-g', "--gamma", default=1, help="(Weighted) frequency that each link of a clique must occur for every delta period in the maximal cliques' timespan", type=float)
    self.parser.add_argument('-v', "--verbose", default=False, help="If set to True additional (progress) information is displayed during runtime")
    self.parser.add_argument('-w', "--weighted", default=False, help="Indicate whether the weights should be used")

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
  # Process command line input to obtain input and output base directories (and other variables)
  input_parser = InputParser()
  args = input_parser.getInputArgumentsAsDict()
  sys.stdout = Logger(args)
  input_parser.printInput()
  start_time = timeit.default_timer()

  # Check valid input provided
  assert os.path.isfile(args["infile"]), "Error: Invalid inputfile specified"
  assert args["delta"] > 0, "Error: delta must be positive"
  os.makedirs(args["outdir"], exist_ok=True)
  outputfile = os.path.join(args["outdir"], "delta-{}-gamma-{}.txt".format(args["delta"], args["gamma"]))

  # Enumerate delta gamma cliques
  Cm = CliqueMaster(args["verbose"])
  Cm.readLinkStream(args["infile"], args["delimiter"], args["weighted"])
  Cm.enumerateDeltaGammaCliques(args["delta"], args["gamma"])
  experiment_compare_stop_time = timeit.default_timer()  # For experiment comparison, we register end time before writing cliques to file
  Cm.printCliques(outputfile)

  #stop_time = timeit.default_timer()
  print("Total runtime: {:.2f}s".format(experiment_compare_stop_time - start_time))
  #print("Total runtime: {:.2f}s".format(stop_time - start_time))
  print("Resources used: {}MB".format(int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)))
  print("Cliques found: {}".format(len(Cm._R)))