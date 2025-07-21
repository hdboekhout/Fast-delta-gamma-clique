"""
MIT License

Copyright (c) 2024 Hanjo Boekhout

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
"""

from Clique import Clique
from CustomNodeLabelling import CustomNodeLabelling

from collections import deque, defaultdict
import bisect
import itertools as it

import sys
import os
import timeit



class CliqueMaster:

  def __init__(self, verbose):
    self._times = defaultdict(list)
    self._weights = defaultdict(list)
    self._nodes = defaultdict(set)

    self._nodeLabelling = CustomNodeLabelling()

    self._time_stretched = defaultdict(list)
    self._tbMins = defaultdict(list)
    self._teMaxs = defaultdict(list)

    self._S = defaultdict(deque) # Stores all size 2 duration-wise maximal (delta,gamma)-cliques
    self._D = set()

    self._R = set()   # Storage of the final result set of (delta,gamma)-maximal cliques

    # Counters and timers to collect statistics on runtime, pruning, and iterations processed.
    self._cut_sub_branches_counter = 0
    self._cut_main_branches_counter = 0
    self._cut_duplicate_branches_counter = 0
    self._iternum = 0

    self._profiling_expansions = 0
    self._profiling_drop = 0
    self._profiling_drop_nl = 0
    self._profiling_drop_nl_counter_yes = 0
    self._profiling_drop_nl_counter_no = 0

    self._verbose = verbose




  #############################################################################################
  # Bulk phase functions
  #############################################################################################

  def isRecursiveOverlapClique(self, c, c_other, delta):
    # First we check if the c and c_other timespans have a valid overlap
    if c._teMax >= c_other._tbMax and c._tbMin <= c_other._teMin:
      new_tbMin = max(c._tbMin, c_other._tbMin)
      new_teMax = min(c._teMax, c_other._teMax)

      overlap = {"tbMin": new_tbMin, "tbMax": new_tbMin + delta - 1,
                 "teMin": new_teMax - delta + 1, "teMax": new_teMax}
    else:
      return []

    # Second we check if the only 'new' link has a valid overlap with the above determined timespan overlap
    link = frozenset([c._latestX, c_other._latestX])

    # Determine first index of stretched times where it's end is late enough to sufficiently overlap with c and c_other
    ind_begin = bisect.bisect_left(self._teMaxs[link], overlap["tbMax"])
    # Determine last index of stretched times where it's beginning is early enough to sufficiently overlap with c and c_other
    ind_end = bisect.bisect_right(self._tbMins[link], overlap["teMin"])
    # Check that there exists at least one clique for this link with some overlap
    if ind_begin >= ind_end:
      return []

    overlaps = []
    # For each clique with an overlap determine the timespan and borders
    for cn in self._time_stretched[link][ind_begin:ind_end]:
      new_tbMin = max(overlap["tbMin"], cn._tbMin)
      new_teMax = min(overlap["teMax"], cn._teMax)

      if c._tb < new_tbMin:
        if c_other._tb < new_tbMin:
          new_tb = c.getMinimumTbFromBorderComb(self._times, new_tbMin, cn._tb, c_other)
        elif cn._tb < new_tbMin:
          new_tb = self._times[link][bisect.bisect_left(self._times[link], new_tbMin):][0]
          new_tb = c.getMinimumTbFromBorderFull(self._times, new_tbMin, min(c_other._tb, new_tb))
        else:
          new_tb = c.getMinimumTbFromBorderFull(self._times, new_tbMin, min(c_other._tb, cn._tb))
      elif c_other._tb < new_tbMin:
        if cn._tb < new_tbMin:
          new_tb = self._times[link][bisect.bisect_left(self._times[link], new_tbMin):][0]
          new_tb = c_other.getMinimumTbFromBorderPart(self._times, new_tbMin, min(c._tb, new_tb))
        else:
          new_tb = c_other.getMinimumTbFromBorderPart(self._times, new_tbMin, min(c._tb, cn._tb))
      elif cn._tb < new_tbMin:
        new_tb = min(c._tb, c_other._tb, self._times[link][bisect.bisect_left(self._times[link], new_tbMin):][0])
      else:
        new_tb = min(c._tb, c_other._tb, cn._tb)

      if c._te > new_teMax:
        if c_other._te > new_teMax:
          new_te = c.getMaximumTeToBorderComb(self._times, cn._te, new_teMax, c_other)
        elif cn._te > new_teMax:
          new_te = self._times[link][:bisect.bisect_right(self._times[link], new_teMax)][-1]
          new_te = c.getMaximumTeToBorderFull(self._times, max(c_other._te, new_te), new_teMax)
        else:
          new_te = c.getMaximumTeToBorderFull(self._times, max(c_other._te, cn._te), new_teMax)
      elif c_other._te > new_teMax:
        if cn._te > new_teMax:
          new_te = self._times[link][:bisect.bisect_right(self._times[link], new_teMax)][-1]
          new_te = c_other.getMaximumTeToBorderPart(self._times, max(c._te, new_te), new_teMax)
        else:
          new_te = c_other.getMaximumTeToBorderPart(self._times, max(c._te, cn._te), new_teMax)
      elif cn._te > new_teMax:
        new_te = max(c._te, c_other._te, self._times[link][:bisect.bisect_right(self._times[link], new_teMax)][-1])
      else:
        new_te = max(c._te, c_other._te, cn._te)

      overlaps.append(((new_tb, new_te), (new_tbMin, new_tbMin + delta - 1, new_teMax - delta + 1, new_teMax), cn))
    return overlaps


  def bulkRecursive(self, delta, c, other_expansions):
    self._iternum += 1

    # Determine further node overlaps
    all_node_expansions = defaultdict(deque)
    all_node_expansions_lists = defaultdict(list)

    start_time = timeit.default_timer()

    extended_borders = {"tbMin": [], "teMax": [], "tbMax": [], "teMin": [], "cov_tb": [], "cov_te": []}
    extended_neighbors = []
    extended_neighbor_indices = []
    extended_node_expansions = defaultdict(list)
    for new_neighbor in self._nodeLabelling.getSortedNodesByLabel(other_expansions.keys()):
      extended = False
      neighbor_E_index = len(extended_borders["tbMin"])

      if c._latestX == new_neighbor:
        continue
      for c_other in other_expansions[new_neighbor]:
        expansions = self.isRecursiveOverlapClique(c, c_other, delta)
        for timespan, borders, cn in expansions:
          # Store node expansions we have found already as Clique objects
          c_new = Clique((frozenset(set(c._X).union([new_neighbor])), timespan), borders,
                          c._shared_neighbors.intersection(self._nodes[new_neighbor]), new_neighbor)
          all_node_expansions[new_neighbor].append(c_new)
          all_node_expansions_lists[new_neighbor].append(c_new)

          if self._nodeLabelling.get(new_neighbor) > self._nodeLabelling.get(c._latestX): # No need to check if we can prune towards branches that must already have already been processed
            extended_node_expansions[new_neighbor].append((c_new, c_other, cn))
            extended_borders["tbMin"].append(c_new._tbMin)
            extended_borders["teMax"].append(c_new._teMax)

            extended_borders["tbMax"].append(c_other._tbMax)
            extended_borders["teMin"].append(c_other._teMin)

            extended = True
      if extended:
        min_tbMax = min(extended_borders["tbMax"])
        max_teMin = max(extended_borders["teMin"])
        extended_neighbors.append(new_neighbor)
        extended_neighbor_indices.append((neighbor_E_index, len(extended_borders["cov_tb"]), min_tbMax, max_teMin))
        # Check not only the cliques which led to extensions but also temporally adjacent ones for potential growth coverage
        for c_other in other_expansions[new_neighbor]:
          if c_other._teMax >= min(extended_borders["tbMax"]) and c_other._tbMin <= max(extended_borders["teMin"]):
            extended_borders["cov_tb"].append(c_other._tb)
            extended_borders["cov_te"].append(c_other._te)

    stop_time = timeit.default_timer()
    self._profiling_expansions += stop_time - start_time
    start_time = timeit.default_timer()

    # Determine which 'other_expansions' are fully dominated by current expansions and can be skipped in the future
    pruning_set = set()
    for n_ind in range(len(extended_neighbors)):
      for (c_new, c_other, cn) in extended_node_expansions[extended_neighbors[n_ind]]:
        if c_other.isTemporallyDominated(c_new._tb, c_new._te):
          (E_key, cov_key, min_tbMax, max_teMin) = extended_neighbor_indices[n_ind]
          E_max_tbMin = max(extended_borders["tbMin"][E_key:])
          E_min_teMax = min(extended_borders["teMax"][E_key:])
          if c_other.isSpatialGrowthDominated(extended_neighbors, self._nodeLabelling) and \
             c_new.isSpatialGrowthReachable(E_max_tbMin, E_min_teMax):
            if n_ind == len(extended_neighbors)-1 or self.isTemporalGrowthDominated(c_other, E_max_tbMin, E_min_teMax, \
                                                                                         min(extended_borders["cov_tb"][cov_key:]), \
                                                                                         max(extended_borders["cov_te"][cov_key:]), \
                                                                                         extended_neighbors[n_ind:], min_tbMax, max_teMin):
              pruning_set.add(c_other)

    stop_time = timeit.default_timer()
    self._profiling_drop += stop_time - start_time

    # Determine based on available expansions if current clique is maximal and recursively try to extend our expansions
    is_max = True
    done_expansions = set()
    for maxX in self._nodeLabelling.getSortedNodesByLabel(all_node_expansions.keys()):
      node_expansions = all_node_expansions[maxX]

      while len(node_expansions) > 0:
        c_new = node_expansions.pop()
        # If an extension exists that maintains or even extends temporal borders, this clique is not maximal
        if is_max and c_new._tb <= c._tb and c._te <= c_new._te:
          is_max = False
        # If this expansion is a duplicate of an earlier processed clique, skip this branch
        if self._nodeLabelling.get(c_new._latestX) <= self._nodeLabelling.get(c._latestX):
          self._cut_duplicate_branches_counter += 1
          continue
        # Check whether this expansion has been pruned
        if c_new in done_expansions:
          self._cut_sub_branches_counter += 1
          continue
        # Continue along this branch of expansion
        valid_expansions = self.bulkRecursive(delta, c_new, all_node_expansions_lists)#_set)
        # Check for all branches to which the recursive call was able to further expand if we can prune them at this level
        for c_valid in valid_expansions:
          done_expansions.add(c_valid)

    # This clique was maximal
    if is_max:
      self._R.add(c)

    return pruning_set



  def isInitialOverlapClique(self, c, u, v, neighbor, delta):
    orig_link = frozenset([u, v])

    # First process adding link (u, neighbor)
    overlaps_u = []

    link_u = frozenset([u, neighbor])
    # Determine first index of stretched times where it's end is late enough to sufficiently overlap with clique
    ind_begin = bisect.bisect_left(self._teMaxs[link_u], c._tbMax)
    # Determine last index of stretched times where it's beginning is early enough to sufficiently overlap with clique
    ind_end = bisect.bisect_right(self._tbMins[link_u], c._teMin)
    # Check that there exists at least one clique for this link with some overlap
    if ind_begin >= ind_end:
      return []

    # For each clique with an overlap determine the timespan and borders
    for cn in self._time_stretched[link_u][ind_begin:ind_end]:
      new_tbMin = max(c._tbMin, cn._tbMin)
      new_teMax = min(c._teMax, cn._teMax)

      overlaps_u.append({"tbMin": new_tbMin, "tbMax": new_tbMin + delta - 1,
                         "teMin": new_teMax - delta + 1, "teMax": new_teMax,
                         "cn_u": cn})

    # Second process adding link (v, neighbor)
    overlaps_uv = []

    link_v = frozenset([v, neighbor])
    for overlap in overlaps_u:
      # Determine first index of stretched times where it's end is late enough to sufficiently overlap with clique
      ind_begin = bisect.bisect_left(self._teMaxs[link_v], overlap["tbMax"])
      # Determine last index of stretched times where it's beginning is early enough to sufficiently overlap with clique
      ind_end = bisect.bisect_right(self._tbMins[link_v], overlap["teMin"])
      # Check that there exists at least one clique for this link with some overlap
      if ind_begin >= ind_end:
        continue

      # For each clique with an overlap determine the timespan and borders
      for cn in self._time_stretched[link_v][ind_begin:ind_end]:
        new_tbMin = max(overlap["tbMin"], cn._tbMin)
        new_teMax = min(overlap["teMax"], cn._teMax)

        orig_tb = c._tb
        if c._tb < new_tbMin:
          orig_tb = self._times[orig_link][bisect.bisect_left(self._times[orig_link], new_tbMin):][0]
        u_tb = overlap["cn_u"]._tb
        if overlap["cn_u"]._tb < new_tbMin:
          u_tb = self._times[link_u][bisect.bisect_left(self._times[link_u], new_tbMin):][0]
        v_tb = cn._tb
        if cn._tb < new_tbMin:
          v_tb = self._times[link_v][bisect.bisect_left(self._times[link_v], new_tbMin):][0]
        new_tb = min(orig_tb, u_tb, v_tb)

        orig_te = c._te
        if c._te > new_teMax:
          orig_te = self._times[orig_link][:bisect.bisect_right(self._times[orig_link], new_teMax)][-1]
        u_te = overlap["cn_u"]._te
        if overlap["cn_u"]._te > new_teMax:
          u_te = self._times[link_u][:bisect.bisect_right(self._times[link_u], new_teMax)][-1]
        v_te = cn._te
        if cn._te > new_teMax:
          v_te = self._times[link_v][:bisect.bisect_right(self._times[link_v], new_teMax)][-1]
        new_te = max(orig_te, u_te, v_te)

        overlaps_uv.append(((new_tb, new_te), (new_tbMin, new_tbMin + delta - 1, new_teMax - delta + 1, new_teMax),
                            {"cn_u": overlap["cn_u"], "cn_v": cn}))

    return overlaps_uv

  def isTemporalGrowthDominated(self, c_other, E_max_tbMin, E_min_teMax, min_cov_tb, max_cov_te, extended_neighbors, min_tbMax, max_teMin):
    # First, we check if the potential growth of c_other can even exceed the minimum potential growth of further extensions.
    # If not, the temporal growth is dominated.
    if E_max_tbMin <= c_other._tbMin and c_other._teMax <= E_min_teMax:
      return True

    # If the temporal growth of c_other can exceed that of the extensions we need to check if it actually ever does.
    # First, we check the actual growth of new shared edges that are covered by the extended cliques here
    if min_cov_tb < E_max_tbMin or E_min_teMax < max_cov_te:
      return False

    start_time = timeit.default_timer()

    # Next we check the actual possible growth through edges between the potential further extension nodes, i.e., the shared edges not covered by the extended cliques
    node_combs = [frozenset([u, v]) for (u,v) in it.combinations(extended_neighbors, 2)]
    for link in node_combs:
      for cn in self._time_stretched[link]:
        # First we check that on the left side, if there is sufficient overlap with the potential growth of c_other AND there is a link earlier than the potential growth of the combined extensions
        if cn._teMax >= min_tbMax and cn._tb < E_max_tbMin:
          stop_time = timeit.default_timer()
          self._profiling_drop_nl += stop_time - start_time
          self._profiling_drop_nl_counter_no += 1
          return False
        # Second we check that on the right side, if there is sufficient overlap with the potential growth of c_other AND there is a link later than the potential growth of the combined extensions
        if cn._tbMin <= max_teMin and cn._te > E_min_teMax:
          stop_time = timeit.default_timer()
          self._profiling_drop_nl += stop_time - start_time
          self._profiling_drop_nl_counter_no += 1
          return False
    self._profiling_drop_nl_counter_yes += 1
    stop_time = timeit.default_timer()
    self._profiling_drop_nl += stop_time - start_time
    return True

  def bulkRecursiveWrapper(self, delta, c, iternum_outer):
    self._iternum += 1
    # Find initial node expansions
    all_node_expansions = defaultdict(deque)
    all_node_expansions_lists = defaultdict(list)

    start_time = timeit.default_timer()

    extended_borders = {"tbMin": [], "teMax": [], "tbMax": [], "teMin": [], "cov_tb": [], "cov_te": []}
    extended_neighbors = []
    extended_neighbor_indices = []
    extended_node_expansions = defaultdict(list)
    [u, v] = list(c._X)
    for neighbor in self._nodeLabelling.getSortedNodesByLabel(list(c._shared_neighbors)):
      extended = False
      neighbor_E_index = len(extended_borders["tbMin"])
      # Compute the node expansions for this neighbor
      expansions = self.isInitialOverlapClique(c, u, v, neighbor, delta)
      for timespan, borders, expansion in expansions:
        # Store node expansions we have found already as Clique objects
        c_new = Clique((frozenset(set(c._X).union([neighbor])), timespan), borders,
                        c._shared_neighbors.intersection(self._nodes[neighbor]), neighbor)
        all_node_expansions[neighbor].append(c_new)
        all_node_expansions_lists[neighbor].append(c_new)

        if self._nodeLabelling.get(neighbor) > self._nodeLabelling.get(c._latestX): # No need to check if we can prune towards branches that must already have already been processed
          extended_node_expansions[neighbor].append((c_new, expansion["cn_u"], expansion["cn_v"]))

          extended_borders["tbMin"].append(c_new._tbMin)
          extended_borders["teMax"].append(c_new._teMax)

          extended_borders["tbMax"].append(expansion["cn_u"]._tbMax)
          extended_borders["tbMax"].append(expansion["cn_v"]._tbMax)
          extended_borders["teMin"].append(expansion["cn_u"]._teMin)
          extended_borders["teMin"].append(expansion["cn_v"]._teMin)

          extended = True
      if extended:
        min_tbMax = min(extended_borders["tbMax"])
        max_teMin = max(extended_borders["teMin"])
        extended_neighbors.append(neighbor)
        extended_neighbor_indices.append((neighbor_E_index, len(extended_borders["cov_tb"]), min_tbMax, max_teMin))

        # Check not only the cliques which led to extensions but also temporally adjacent ones for potential growth coverage
        link_u = frozenset([u, neighbor])
        for cn in self._time_stretched[link_u][bisect.bisect_left(self._teMaxs[link_u], min_tbMax):bisect.bisect_right(self._tbMins[link_u], max_teMin)]:
          extended_borders["cov_tb"].append(cn._tb)
          extended_borders["cov_te"].append(cn._te)
        link_v = frozenset([v, neighbor])
        for cn in self._time_stretched[link_v][bisect.bisect_left(self._teMaxs[link_v], min_tbMax):bisect.bisect_right(self._tbMins[link_v], max_teMin)]:
          extended_borders["cov_tb"].append(cn._tb)
          extended_borders["cov_te"].append(cn._te)

    stop_time = timeit.default_timer()
    self._profiling_expansions += stop_time - start_time
    start_time = timeit.default_timer()

    # Determine which neighboring links are fully dominated by current expansions and can be skipped in the future
    for n_ind in range(len(extended_neighbors)):
      for (c_new, c_u, c_v) in extended_node_expansions[extended_neighbors[n_ind]]:
        if c_u not in self._D: # Prevent rechecking an already pruned 2-node clique
          if c_u.isTemporallyDominated(c_new._tb, c_new._te):
            (E_key, cov_key, min_tbMax, max_teMin) = extended_neighbor_indices[n_ind]
            E_max_tbMin = max(extended_borders["tbMin"][E_key:])
            E_min_teMax = min(extended_borders["teMax"][E_key:])
            if c_u.isSpatialGrowthDominated(extended_neighbors, self._nodeLabelling) and \
               c_new.isSpatialGrowthReachable(E_max_tbMin, E_min_teMax):
              if n_ind == len(extended_neighbors)-1 or self.isTemporalGrowthDominated(c_u, E_max_tbMin, E_min_teMax, \
                                                                                           min(extended_borders["cov_tb"][cov_key:]), \
                                                                                           max(extended_borders["cov_te"][cov_key:]), \
                                                                                           extended_neighbors[n_ind:], min_tbMax, max_teMin):
                self._D.add(c_u)
        if c_v not in self._D: # Prevent rechecking an already pruned 2-node clique
          if c_v.isTemporallyDominated(c_new._tb, c_new._te):
            (E_key, cov_key, min_tbMax, max_teMin) = extended_neighbor_indices[n_ind]
            E_max_tbMin = max(extended_borders["tbMin"][E_key:])
            E_min_teMax = min(extended_borders["teMax"][E_key:])
            if c_v.isSpatialGrowthDominated(extended_neighbors, self._nodeLabelling) and \
               c_new.isSpatialGrowthReachable(E_max_tbMin, E_min_teMax):
              if n_ind == len(extended_neighbors)-1 or self.isTemporalGrowthDominated(c_v, E_max_tbMin, E_min_teMax, \
                                                                                           min(extended_borders["cov_tb"][cov_key:]), \
                                                                                           max(extended_borders["cov_te"][cov_key:]), \
                                                                                           extended_neighbors[n_ind:], min_tbMax, max_teMin):
                self._D.add(c_v)

    stop_time = timeit.default_timer()
    self._profiling_drop += stop_time - start_time

    # Determine based on available expansions if current clique is maximal and recursively try to extend our expansions
    is_max = True
    done_expansions = set()
    for maxX in self._nodeLabelling.getSortedNodesByLabel(all_node_expansions.keys()):
      node_expansions = all_node_expansions[maxX]

      while len(node_expansions) > 0:
        c_new = node_expansions.pop()
        # If an extension exist that maintains or even extends temporal borders, this clique is not maximal
        if is_max and c_new._tb <= c._tb and c._te <= c_new._te:
          is_max = False
        # If this expansion is a duplicate of an earlier processed clique, skip this branch
        if self._nodeLabelling.get(c_new._latestX) <= self._nodeLabelling.get(c._latestX):
          self._cut_duplicate_branches_counter += 1
          continue
        # Check whether this expansion has been pruned
        if c_new in done_expansions:
          self._cut_sub_branches_counter += 1
          continue

        # Continue along this branch of expansion
        valid_expansions = self.bulkRecursive(delta, c_new, all_node_expansions_lists)#_set)
        # Check for all branches to which the recursive call was able to further expand if we can prune them at this level
        for c_valid in valid_expansions:
          done_expansions.add(c_valid)

    # This clique was maximal
    if is_max:
      self._R.add(c)


  def bulkPhase(self, delta):
    iternum_outer = 0

    for maxX in self._nodeLabelling.getSortedNodesByLabel(self._S.keys()):
      S = self._S[maxX]

      while len(S) > 0:
        iternum_outer += 1
        c = S.pop()

        # Check whether clique c has been pruned
        if c in self._D:
          self._cut_main_branches_counter += 1
          continue

        self.bulkRecursiveWrapper(delta, c, iternum_outer)

        if self._verbose:
          sys.stderr.write("Found {} unique maximal, {} processed, {} iter, {} main cut, {} sub cut, {} sub dupl\r".format(len(self._R), iternum_outer, self._iternum, self._cut_main_branches_counter, self._cut_sub_branches_counter, self._cut_duplicate_branches_counter))

    sys.stdout.write("Found {} unique maximal, {} processed, {} iter, {} main cut, {} sub cut, {} sub dupl\n".format(len(self._R), iternum_outer, self._iternum, self._cut_main_branches_counter, self._cut_sub_branches_counter, self._cut_duplicate_branches_counter))

  #############################################################################################
  # Link stream reading in functions
  #############################################################################################

  def readUnweightedLinkStream(self, infile, delimiter):
    with open(infile) as inf:
      for line in inf:
        contents = line.split(delimiter)
        t = int(contents[0])
        u = int(contents[1])
        v = int(contents[2])

        link = frozenset([u, v])
        self._times[link].append(t)
        self._weights[link].append(1)
        self._nodes[u].add(v)
        self._nodes[v].add(u)

  def readWeightedLinkStream(self, infile, delimiter):
    with open(infile) as inf:
      for line in inf:
        contents = line.split(delimiter)
        t = int(contents[0])
        u = int(contents[1])
        v = int(contents[2])
        w = float(contents[3])

        link = frozenset([u, v])
        self._times[link].append(t)
        self._weights[link].append(w)
        self._nodes[u].add(v)
        self._nodes[v].add(u)

  def readLinkStream(self, infile, delimiter=" ", weighted=False):
    # Check if input file actually exists
    assert os.path.isfile(infile), "Error (1): Invalid inputfile specified"
    # Reset the various storage data structures
    self._times.clear()
    self._weights.clear()
    self._nodes.clear()

    # Open file to check valid format (based on first line) and whether weighted or not to call the appropriate function
    with open(infile) as inf:
      first_line = inf.readline()
      contents = first_line.split(delimiter)
      if weighted:
        assert len(contents) == 4, "Error (2): Too few columns. Expected format is '<timestamp> <node_identifier> <node_identifier> <weight>'"
        assert len(contents) < 5, "Error (3): Too many columns. Expected format is '<timestamp> <node_identifier> <node_identifier> <weight>'"
      else:
        assert len(contents) >= 3, "Error (2): Too few columns. Expected format is '<timestamp> <node_identifier> <node_identifier> <optional weight>'"
        assert len(contents) < 5, "Error (3): Too many columns. Expected format is '<timestamp> <node_identifier> <node_identifier> <optional weight>'"

    if weighted:
      self.readWeightedLinkStream(infile, delimiter)
    else:
      self.readUnweightedLinkStream(infile, delimiter)

  #############################################################################################
  # Stretch phase functions, with an O(m) guaranteed implementation
  #############################################################################################

  def addStretchedClique(self, c):
    # Store the clique in the appropriate data structures
    self._time_stretched[c._X].append(c)
    self._tbMins[c._X].append(c._tbMin)
    self._teMaxs[c._X].append(c._teMax)
    # Determine shared neighbors and add clique to the relevant deque
    c.setSharedNeighbors(self._nodes)
    self._S[c._latestX].append(c)


  def stretchRight(self, link, delta, gamma):
    times = self._times[link]
    weights = self._weights[link]
    elems = len(times)

    begin_index = 0
    end_index = 0
    current_weight = weights[begin_index]

    while True:
      # Find the next stretch (begin_index, end_index) which has a cumulative weight greater or equal to gamma
      while current_weight < gamma:
        end_index += 1
        if end_index == elems:
          return
        # If we exceed delta before achieving gamma weight, we move the begin_index one forward
        while times[end_index] - times[begin_index] >= delta:
          current_weight -= weights[begin_index]
          begin_index += 1
        current_weight += weights[end_index]
      tb = times[begin_index]  # However long the stretch goes on, this will be the first link
      tbMax = times[end_index] # We know this is the first time that gamma is exceeded

      done = False
      while not done:
        temp_b = begin_index
        temp_e = end_index
        # Stretch end_index as far as delta allows
        while end_index + 1 < elems and times[end_index + 1] - times[begin_index] < delta:
          end_index += 1
          current_weight += weights[end_index]
        # Next we move the begin_index far enough to the right such that we find the last time that (begin_index, end_index) still exceeds or is equal to gamma
        while begin_index + 1 <= end_index and current_weight - weights[begin_index] >= gamma:
          current_weight -= weights[begin_index]
          begin_index += 1
        # If we have stretched as far as the final link instance, save Clique and return
        if end_index + 1 == elems:
          c_new = Clique((link, (tb, times[end_index])), (tbMax - delta + 1, tbMax, times[begin_index], times[begin_index] + delta - 1),
                         latest=self._nodeLabelling.maxLabelledNode(link))
          self.addStretchedClique(c_new)
          return

        # If indices did not move, check if from times[begin_index] + 1, we can still obtain a gamma weight again within delta time
        if begin_index == temp_b and end_index == temp_e:
          temp_begin = times[begin_index] + 1
          current_weight -= weights[begin_index]

          temp_end_index = end_index
          while current_weight < gamma:
            temp_end_index += 1
            # If not found while we have arrived at the final instance, store current Clique and finish search
            if temp_end_index == elems:
              c_new = Clique((link, (tb, times[end_index])), (tbMax - delta + 1, tbMax, times[begin_index], times[begin_index] + delta - 1),
                             latest=self._nodeLabelling.maxLabelledNode(link))
              self.addStretchedClique(c_new)
              return
            # If we exceed delta before achieving gamma weight, we store the current Clique and continue new search from begin_index + 1 (which may or may not be larger than times[begin_index] + 1, and set end_index to previous value for which we still checked that we were under gamma weight and within delta time)
            if times[temp_end_index] - temp_begin >= delta:
              c_new = Clique((link, (tb, times[end_index])), (tbMax - delta + 1, tbMax, times[begin_index], times[begin_index] + delta - 1),
                             latest=self._nodeLabelling.maxLabelledNode(link))
              self.addStretchedClique(c_new)
              temp_end_index -= 1
              done = True
              break
            current_weight += weights[temp_end_index]
          # Either way our search continues from begin_index + 1
          begin_index += 1
          # Whether we continue search for the same clique or a new clique we do not want to throw away already searched parts
          end_index = temp_end_index # Continue search for expansion beyond where was already searched


  def stretchPhase(self, delta, gamma):
    # If delta is 0 we are looking for static cliques only, so no growth in time spans possible
    if delta > 0:
      for link in self._times.keys():
        # Skip any links whose total weight is smaller than gamma
        if sum(self._weights[link]) < gamma:
          continue
        # Continuously Stretch to the right as far as possible to form all delta-maximal size 2 cliques for this link
        self.stretchRight(link, delta, gamma)
    self._weights.clear() # Free up this memory as we no longer need to consider it for the bulk phase

  #############################################################################################
  # Delta gamma enumeration functions
  #############################################################################################

  def enumerateDeltaGammaCliques(self, delta, gamma):
    print("Create node labelling...", end='\r')
    start_time = timeit.default_timer()
    self._nodeLabelling.createNodeLabelling(self._nodes)
    stop_time = timeit.default_timer()
    print("Create node labelling... completed in {} seconds".format(stop_time - start_time))

    print("Stretch phase...", end='\r')
    start_time = timeit.default_timer()
    self.stretchPhase(delta, gamma)
    stop_time = timeit.default_timer()
    print("Stretch phase... completed in {} seconds".format(stop_time - start_time))

    if self._verbose:
      total_stretched_cliques = 0
      for key, values in self._S.items():
        total_stretched_cliques += len(values)
      print("Total duration-wise maximal 2-node (delta,gamma)-cliques found: {}".format(total_stretched_cliques))

    print("Bulk phase...")
    start_time = timeit.default_timer()
    self.bulkPhase(delta)
    stop_time = timeit.default_timer()
    print("Bulk phase... completed in {} seconds".format(stop_time - start_time))
    print("Time spent on expansion computation: {} seconds".format(self._profiling_expansions))
    print("Time spent on drop evaluation: {} seconds".format(self._profiling_drop))
    print("Time spent on drop new neigbhor link evaluation: {} seconds".format(self._profiling_drop_nl))
    print("Number of times cuts applied/not applied due to new neigbhor link evaluation: {}/{}".format(self._profiling_drop_nl_counter_yes, self._profiling_drop_nl_counter_no))

    #return self._R

  #############################################################################################
  # Clique output/printing related functions
  #############################################################################################

  def printCliques(self, outputfile):
    with open(outputfile, 'w') as out:
      for c in list(self._R):
        out.write(str(c) + "\n")

  def __str__(self):
    msg = ""
    for c in self._R:
      msg += str(c) + "\n"
    return msg
