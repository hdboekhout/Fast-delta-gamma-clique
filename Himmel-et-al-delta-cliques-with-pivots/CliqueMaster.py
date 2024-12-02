'''
    Temporal cliques: Enumerating delta-cliques in temporal graphs. 
    Copyright (C) 2016 Anne-Sophie Himmel
    For licensing see COPYING.
'''

import sys, time
import copy
from Clique import Clique
from Neighborhood import Neighborhood
import Pivoting
from collections import defaultdict

class CliqueMaster:

    def __init__(self, G, vertices, firstEdge, lastEdge, delta, pivoting_lvl):
        self.begin = firstEdge
        self.lifetime = lastEdge - firstEdge
        self.vertices = vertices
        self.delta = delta
        self.pivoting_lvl = pivoting_lvl
        self.neighborhood = Neighborhood(G, self.begin,  self.lifetime, delta)
        self.maxCliques = set()

        self.callCounter = 0
        # if set() datastructure used - unnecessarily
        #self.maxCliques = set()
        self.BronKerboschDelta()
        print("# function calls: " + str(self.callCounter))

    def __str__(self):
        msg = ""
        for c in self.maxCliques:
            msg += str(c) + "\n"
        return msg

    # initial call
    def BronKerboschDelta(self):
        R = Clique(set(), (self.begin, self.begin + self.lifetime))
        Pmax = self.vertices
        Xmax = set()
        P = dict()
        X = dict()

        for v in self.vertices:
            P[v] = [(self.begin, self.begin + self.lifetime)]

        t1 = time.time()
        self.BronKerboschDeltaRecursive(Pmax, P, R, Xmax, X)
        t2 = time.time()
#               sys.stdout.write("Time to calculate cliques with Pivoting: %s seconds \n" % (t2 - t1))


    def BronKerboschDeltaRecursive(self, Pmax, P, R, Xmax, X):
        self.callCounter += 1
        #check for max Clique
        if not Pmax and not Xmax and (len(R.R) > 1):
            self.addClique(R)

        #get pivot elements and corresponding dismiss elements

        #dismiss = Pivoting.pivotingHeuristic(pivots, pivotIntervals)
        dismiss = []

        if self.pivoting_lvl > 0:
            pivots, pivotIntervals = self.neighborhood.computePivotInformation(copy.deepcopy(P))

            if len(pivots) > 1:
                if self.pivoting_lvl == 1:
                    dismiss = Pivoting.pivotingOne(pivots, pivotIntervals)
                elif self.pivoting_lvl == 2:
                    dismiss = Pivoting.pivotingOneMax(pivots, pivotIntervals)
                elif self.pivoting_lvl == 3:
                    dismiss = Pivoting.pivotingMany(pivots, pivotIntervals)
                elif self.pivoting_lvl == 4:
                    dismiss = Pivoting.pivotingGreedy(pivots, pivotIntervals)
                elif self.pivoting_lvl == 5:
                    dismiss = Pivoting.pivotingOptimal(pivots, pivotIntervals)
            elif len(pivots) == 1:
                _, dismiss = pivots.popitem()

        P_support = copy.deepcopy(P)
        while len(P_support) != 0:
            v = list(P_support.keys())[0]

            if v not in X: X[v] = []

            while len(P_support[v]) != 0:
                interval = P_support[v][0]
                if (v, interval) not in dismiss:
                    # update clique
                    R_new = copy.deepcopy(R)
                    R_new.expandClique(v, interval)
                    # compute neighborhood of new delta clique
                    P_new, Pmax_new = self.neighborhood.cut((v, interval), copy.deepcopy(P))
                    X_new, Xmax_new = self.neighborhood.cut((v, interval), copy.deepcopy(X))
                    # recursive function call
                    self.BronKerboschDeltaRecursive(Pmax_new, P_new, R_new, Xmax_new, X_new)
                    # remove interval from P to X
                    P[v].remove(interval)
                    X[v].append(interval)
                    X[v] = sorted(X[v], key=lambda Interval: Interval[0])
                P_support[v].remove(interval)
            del P_support[v]
            if len(P[v]) == 0: del P[v]
            if len(X[v]) == 0: del X[v]


    def addClique(self, R):
        #self.maxCliques.append(R)
        # if sest() datastructure used - unnecessarily
        self.maxCliques.add(R)

    def addCliquePivoting(self, R):
        #self.maxCliquesPivoting.append(R)
        # if sest() datastructure used - unnecessarily
        self.maxCliquesPivoting.add(R)


    def maxCliqueSize(self):
        maxSize = 0
        for R in self.maxCliques:
            maxSize = max(len(R.R), maxSize)
        return maxSize

    def cliqueSizes(self):
        maxSize = self.maxCliqueSize()
        listCliqueSize = []
        # create list
        for i in range(maxSize):
            listCliqueSize.append(0)
        # fill list
        for R in self.maxCliques:
            listCliqueSize[len(R.R)-1] += 1
        return listCliqueSize

    def average_clique_size(self):
        cumulative_size = 0
        for c in self.maxCliques:
            cumulative_size += len(c.R)
        return float(cumulative_size) / float(len(self.maxCliques))

    def max_clique_length(self):
        max_length = 0
        for c in self.maxCliques:
            max_length = max(max_length, c.endInterval - c.startInterval)
        return max_length

    def average_clique_length(self):
        cumulative_length = 0
        for c in self.maxCliques:
            cumulative_length += c.endInterval - c.startInterval
        return float(cumulative_length) / float(len(self.maxCliques))

    ##############################################################
    # Added by [Boekhout, 2024] for post-processing
    ##############################################################
    def checkSubclique(self, c, max_mem_size, border_reduc_maxCliques, index_dict):
        c_mem_size = len(c.R)

        for o_mem_size in range(c_mem_size+1, max_mem_size+1):
            # Determine all indices with at least one overlap member
            all_larger_indices = set()
            for c_member in list(c.R):
                all_larger_indices.update(index_dict[o_mem_size][c_member])
            # Loop over all such indices to determine larger cliques that fully overlap clique c
            for o_ind in sorted(list(all_larger_indices)):
                other = border_reduc_maxCliques[o_ind]
                if len(set(c.R) - set(other.R)) == 0:
                    # Check if c is also temporally dominated by other
                    if other.startInterval <= c.startInterval and c.endInterval <= other.endInterval:
                        return False
        return True

    def postProcess(self, times):
        if len(self.maxCliques) == 0:
            return
        # First we update the borders to their borders according to the Boekhout & Takes definition
        old_maxCliques = list(self.maxCliques)
        border_reduc_maxCliques = []
        index_dict = defaultdict(lambda: defaultdict(set))
        cur_ind = 0
        self.maxCliques.clear()
        for c in old_maxCliques:
            c.setTrueBorders(times)
            border_reduc_maxCliques.append(c)
            for member in list(c.R):
                index_dict[len(c.R)][member].add(cur_ind)
            cur_ind += 1

        # Then we determine for each clique if it has remained maximal
        max_mem_size = max(index_dict.keys())
        for c_ind in range(len(border_reduc_maxCliques)):
            c = border_reduc_maxCliques[c_ind]
            if self.checkSubclique(c, max_mem_size, border_reduc_maxCliques, index_dict):
                self.maxCliques.add(c)
    ##############################################################