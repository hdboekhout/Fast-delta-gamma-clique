'''
    Temporal cliques: Enumerating delta-cliques in temporal graphs. 
    Copyright (C) 2016 Anne-Sophie Himmel
    For licensing see COPYING.
'''
import bisect
import itertools as it

class Clique:

    def __init__(self, V, I):
        (start, end) = I;
        self.R = frozenset(V);
        self.startInterval = start;
        self.endInterval = end;

    def __eq__(self, other):
        return self.R == other.R and self.startInterval == other.startInterval and self.endInterval == other.endInterval

    def __hash__(self):
        return hash((self.R,self.startInterval, self.endInterval))

    def __str__(self):
        return "{"+','.join(map(str, list(self.R))) + "} (" + str(self.startInterval) + "," + str(self.endInterval)+")"

    def expandClique(self, v, I):
        (start, end) = I
        self.R |= frozenset([v])
        if start <= end:
            self.startInterval = start
            self.endInterval = end

    def expandCliqueByVertex(self, v):
        self.R |= frozenset([v])

        def size(self):
                return len(self.R)

    ##############################################################
    # Added by [Boekhout, 2024] for post-processing
    ##############################################################
    def setTrueBorders(self, times):
        tbMin = self.startInterval
        teMax = self.endInterval

        # Set values to extreme on the other end
        startInterval = teMax
        endInterval = tbMin
        # Update borders to the first and last instance of any link found within timespan
        node_combs = [frozenset([u, v]) for (u,v) in it.combinations(self.R, 2)]
        for link in node_combs:
            time = times[link][bisect.bisect_left(times[link], tbMin):bisect.bisect_right(times[link], teMax)]
            startInterval = min(startInterval, time[0])
            endInterval = max(endInterval, time[-1])

        self.startInterval = startInterval
        self.endInterval = endInterval
    ##############################################################
