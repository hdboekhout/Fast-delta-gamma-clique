'''
    Temporal cliques: Enumerating delta-cliques in temporal graphs. 
    Copyright (C) 2016 Anne-Sophie Himmel
    For licensing see COPYING.
'''

from DeltaInterval import DeltaInterval
import sys

class Neighborhood:

    # Initiates Neighborhood by examining the whole graph G
    def __init__(self, G, begin, lifetime, delta):
        self.delta = delta
        self.begin = begin
        self.lifetime = lifetime
        self.neighborhood = dict()
        self.neighbors = dict()
        self.vertexActivity = dict()
        self.computeNeighborhood(G)
        #self.neighborhood, self.vertexActivity = self.computeNeighborhood(G);
        #self.neighborhood, self.neighbors, self.vertexActivity = self.computeNeighborhoodA(G)

    def __eq__(self, other):
        return self.neighborhood == other.neighborhood and self.delta == other.delta and self.lifetime == other.lifetime

    # Helper function: computes all intervals during which the two
    # vertices are neighbors based on the edges between these
    # vertices
        # return type: dict
    def computeNeighborhood(self, G):
        neighbors = G
        for vw in neighbors.keys():
            if len(vw) > 1:
                intervals = []
                edgeList = sorted(neighbors[vw])

                start = max(self.begin, edgeList.pop(0) - self.delta)
                end = min(self.begin + self.lifetime, start + self.delta * 2)
                for t in edgeList:
                    if (end+1) < t:
                        intervals.append((start,end))
                        start = max(self.begin, t - self.delta)
                        end = min(self.begin + self.lifetime,t + self.delta)
                    else:
                        end = min(self.begin + self.lifetime, t + self.delta)
                intervals.append((start,end))
                self.neighborhood[vw] = intervals

                vwList = list(vw)
                for i in range(len(vwList)):
                    if vwList[i] not in self.neighbors:
                        self.neighbors[vwList[i]] = [vwList[(i + 1) % 2]]
                    else:
                        self.neighbors[vwList[i]].append(vwList[(i + 1) % 2])

    def returnNeighborhood(self, clique):
        (v, (start, end)) = clique
        neighborhood = dict()
        if v in self.neighbors:
            for w in self.neighbors[v]:
                counter = self.deltaNeighborhood(start, end, self.neighborhood[frozenset([v,w])])
                if counter > 0:
                    neighborhood[w] = counter
        return neighborhood

    # Helper function to compute the intersection of intervals in two lists
    def deltaNeighborhood(self, start, end, neigborhoodList):
        counter = 0
        #list_new = []
        curr = 0

        while curr < len(neigborhoodList):
            (i_start, i_end) = neigborhoodList[curr]
            if end < (i_start + self.delta):
                break
            if i_end < (start + self.delta):
                curr += 1
                continue
            else:
                a = max(i_start, start)
                b = min(i_end, end)
                counter += 1
                #list_new.append((a,b))
                curr += 1
                continue

        return counter

    # compute the cut
    # return P, Pmax
    def cut(self, clique, P):
        (v, (start, end)) = clique
        Pmax = set()
        Pkeys = list(P.keys())
        for w in Pkeys:
            if frozenset([v,w]) in self.neighborhood:
                # get intersection of both tree within interval (start, end)
                P[w], P_supp = self.deltaIntersect(start, end, P[w], self.neighborhood[frozenset([v,w])])
                if P_supp:
                    Pmax.add(w)
                # check if still intervals exist
                if len(P[w]) == 0:
                    del P[w]
            else:
                del P[w]

        # return new P and Pmax
        return P, Pmax


    # helper function to compute the intersection of intervals in two lists
    def deltaIntersect(self, start, end, list1, list2):
        list_new = []
        list1_curr = 0
        list2_curr = 0

        while list1_curr < len(list1) and list2_curr < len(list2):
            (i1_start, i1_end) = list1[list1_curr]
            if end < (i1_start + self.delta):
                break
            if i1_end < (start + self.delta):
                list1_curr += 1
                continue
            else:
                while list2_curr < len(list2):
                    (i2_start, i2_end) = list2[list2_curr]

                    if i2_end < (start + self.delta):
                        list2_curr += 1
                        continue
                    if end < (i2_start + self.delta):
                        list2_curr = len(list2)
                        break
                    if i2_end < (i1_start + self.delta):
                        list2_curr += 1
                        continue
                    if i2_start < i1_start and i2_end > i1_start and i2_end <= i1_end:
                        a = max(i1_start, start)
                        b = min(i2_end, end)
                        if b - a >= self.delta:
                            list_new.append((a,b))
                        list2_curr += 1
                        continue

                    if i2_start < i1_start and i2_end > i1_end:
                        a = max(i1_start, start)
                        b = min(i1_end, end)
                        if b - a >= self.delta:
                            list_new.append((a,b))
                        list1_curr += 1
                        break

                    if i2_start >= i1_start and i2_end <= i1_end:
                        a = max(i2_start, start)
                        b = min(i2_end, end)
                        if b - a >= self.delta:
                            list_new.append((a,b))
                        list2_curr += 1
                        continue

                    if i2_start >= i1_start and i2_start < i1_end and i2_end > i1_end:
                        a = max(i2_start, start)
                        b = min(i1_end, end)
                        if b - a >= self.delta:
                            list_new.append((a,b))
                        list1_curr += 1
                        break

                    if i2_start >= i1_end:
                        list1_curr += 1
                        break
        Pmax = False
        if len(list_new) == 1 and list_new[0] == (start,end):
            Pmax = True

        return list_new, Pmax


    def union(self):
        union = dict()
        for vw in self.neighborhood.keys():
            for v in vw:
                union[v] = neighborhood[vw]

    def computePivotInformation(self, P):
        pivot = dict()
        pivotIntervals = []
        for v in P:
            for I in P[v]:
                pivot[(v,I)] = set()
                for w in P:
                    if w != v:
                        tmp = self.checkIn((w, P[w]), (v, I))
                        pivot[(v,I)].update(tmp)
                if len(pivot[(v,I)]) == 0:
                    del pivot[(v,I)]
                else:
                    pivotIntervals.append(DeltaInterval((v,I), pivot[(v,I)]))
        return pivot, pivotIntervals

    def checkIn(self, cand_ext, clique):
        (v, (start, end)) = clique
        (w, list1) = cand_ext


        pivot = set()
        if frozenset([v,w]) in self.neighborhood:
            '''
            list2 = self.neighborhood[frozenset([v,w])]
            for (start1, end1) in list1:
                if start1 >= start and end1 <= end:
                    for (start2, end2) in list2:
                        if start1 >= start2 and end1 <= end2:
                            pivot.add((w,(start1, end1)))

            '''
            list2 = self.neighborhood[frozenset([v,w])]
            list1_curr = 0
            list2_curr = 0
            while list1_curr < len(list1) and list2_curr < len(list2):
                (i1_start, i1_end) = list1[list1_curr]
                if end < i1_end or start > i1_start:
                    break
                else:
                    while list2_curr < len(list2):
                        (i2_start, i2_end) = list2[list2_curr]
                        if i1_start >= i2_start and i1_end <= i2_end:
                            pivot.add((w,(i1_start, i1_end)))
                            list1_curr += 1
                            break
                        if i1_start < i2_start and i1_end > i2_end:
                            list1_curr += 1
                            list2_curr += 1
                            break
                        if i1_start < i2_start:
                            list1_curr += 1
                            break
                        if i1_end > i2_end:
                            list2_curr += 1
                            continue

        return pivot
