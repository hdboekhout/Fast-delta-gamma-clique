from CliqueMaster_m import CliqueMaster
from Clique_m import Clique
import sys
import networkx as nx
import bisect
import time as TM
import os
#import psutil

import argparse
import resource
import timeit

#############################################################################################
# Logger functions  (added by [Boekhout, 2024] for performance logging)
#############################################################################################

class Logger(object):
  def __init__(self, args):
    self.terminal = sys.stdout
    os.makedirs("logfiles-clique-enumeration", exist_ok=True)
    base_name = "logfiles-clique-enumeration/logfile-Banerjee-Pal-{}_d{}_g{}".format(args["infile"].split("/")[-1],
                                                                                     args["delta"], args["gamma"])
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
    #self.printInput()

  def setArguments(self):
    self.parser.add_argument('-in', "--infile", required=True, help="Location of link stream input file, requiring format '<timestamp> <node_identifier> <node_identifier> <optional weight>'")
    self.parser.add_argument('-out', "--outdir", required=True, help="Location of directory in which output files will be stored for the enumerated delta-gamma-maximal cliques")
    self.parser.add_argument('-l', "--delimiter", default=" ", help="Delimiter used between columns of link stream input file")
    self.parser.add_argument('-d', "--delta", default=1, help="Maximum time period within which there must always be a (weighted) frequency of gamma of each link of a clique to be maximal", type=int)
    self.parser.add_argument('-g', "--gamma", default=1, help="Frequency that each link of a clique must occur for every delta period in the maximal cliques' timespan", type=int)

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
  assert args["gamma"] >= 0, "Gamma must be positive."
  gamma = args["gamma"]
  os.makedirs(args["outdir"], exist_ok=True)
  output_file = os.path.join(args["outdir"], "delta-{}-gamma-{}.txt".format(args["delta"], args["gamma"]))
  start_time = timeit.default_timer()
  ##############################################################

  # Initiate
  Cm = CliqueMaster()
  times = dict()
  nodes = dict()
  nb_lines = 0
  resurrect = False

  # Create Graph
  G = nx.Graph()
  # Read stream
  #for line in sys.stdin:
  #start_time = TM.time()
  with open(args["infile"], 'r') as inf:
    for line in inf:
      contents = line.split(" ")
      t = int(contents[0])
      u = contents[1].strip()
      v = contents[2].strip()

      link = frozenset([u, v])
      time = (t, t)

      ##Add the edge in the static graph G
      G.add_edge(str(u), str(v))

      # This a new instance
      #Cm.addClique(Clique((link, time), set([])))

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
  Cm._graph = G
  sys.stderr.write("Processed " + str(nb_lines) + " from stdin\n")

  #print("Size of Graph:", sys.getsizeof(G)/1024)

  ##### Bithika:

  for e in G.edges():
    #print(e[0],e[1]) #### ----------------- print removed 12122019
    #print(times[frozenset([e[0],e[1]])])
    temp_ts = times[frozenset([e[0],e[1]])]
    X = set([e[0],e[1]])
    Y = set(list(G.neighbors(e[0])))
    Z = set(list(G.neighbors(e[1])))
    neighborlist = (Y.intersection(Z))-X
    #print('X: ', X, 'Y: ',Y, 'Z: ', Z, 'neighborlist: ', neighborlist)
    if len(temp_ts) >= gamma:
      for i in range(len(temp_ts)):
        if i == 0:
          current_list = []
          current_list.append(temp_ts[i])
          #print(current_list, i)
          #print('if : case 1')
        elif len(current_list) < gamma:
          if (temp_ts[i] - current_list[0]) <= delta:
            current_list.append(temp_ts[i])
            #print(current_list, i)
            #print('elif : case 2')
          else:
            link = frozenset([e[0], e[1]])
            current_list = []
            links_1 = times[link][bisect.bisect_left(times[link], temp_ts[i] - delta):bisect.bisect_left(times[link], temp_ts[i])+1]
            for l in links_1:
              current_list.append(l)

        elif len(current_list) >= gamma :
          if (current_list[len(current_list)-gamma]+1+delta) >= temp_ts[i]:
          #if (temp_ts[i] - temp_ts[i-gamma+1]) <= delta:
            current_list.append(temp_ts[i])
          else:
            tb = current_list[gamma-1] - delta
            te = current_list[len(current_list) - gamma] + delta
            link = frozenset([e[0], e[1]])
            time = (tb,te)
            Cm.addClique(Clique((link, time), neighborlist))   ### neighborlist
            current_list = []
            links_1 = times[link][bisect.bisect_left(times[link], temp_ts[i] - delta):bisect.bisect_left(times[link], temp_ts[i])+1]
            for l in links_1:
              current_list.append(l)
              #print(current_list, i)
              #print('elif else : case 4')
        #else:
          #None

        if (i== len(temp_ts)-1) and len(current_list) >= gamma:
          #print(current_list, i)
          tb = current_list[0+gamma-1] - delta
          te = current_list[len(current_list) - gamma] + delta
          link = frozenset([e[0], e[1]])
          time = (tb,te)
          #print(link,time)
          Cm.addClique(Clique((link, time), neighborlist))   #### neighborlist
          current_list = []
          #print('if : case 6')

  for c in Cm._S:
    if frozenset(c._X) in Cm._clique_dict:
      Cm._clique_dict[frozenset(c._X)].append((c._tb,c._te))
    else:
      Cm._clique_dict[frozenset(c._X)] = []
      Cm._clique_dict[frozenset(c._X)].append((c._tb,c._te))


  #Cm.printInitialCliques()
  Cm.getDeltaGammaCliques(delta, gamma)

  ##############################################################
  # Added/updated by [Boekhout, 2024] for post-processing and consistent performance logging
  ##############################################################
  stop_time = timeit.default_timer()
  print("Total runtime (before post processing): {:.2f}s".format(stop_time - start_time))
  print("Resources used (before post processing): {}MB".format(int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)))
  print("Cliques found (before post processing): {}".format(len(Cm._R)))
  Cm.postProcess()
  Cm.printCliques(output_file)

  if len(Cm._R) > 0:
    # end_time = TM.time()
    # print("Number of cliques: ", str(len(Cm._R)) )
    # print("Delta: ", str(delta) )
    # print("Max cardinality: ", str(Cm._maxsize))
    # print("Max duration: ", str(Cm._maxdur))
    print("Number of iterations: ", str(Cm._iternum))
    # print("Computational Time: ", end_time - start_time)
    # process = psutil.Process(os.getpid())
    # print("Used Memory:", process.memory_info().rss/1024/1024, "MB")  # in bytes

  stop_time = timeit.default_timer()

  print("Total runtime: {:.2f}s".format(stop_time - start_time))
  print("Resources used: {}MB".format(int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)))
  print("Cliques found: {}".format(len(Cm._R)))
  ##############################################################
