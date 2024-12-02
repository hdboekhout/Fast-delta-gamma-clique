# -*-coding:utf8*-
import sys
from collections import deque, defaultdict
from Clique import Clique
import itertools as it

class CliqueMaster:

    def __init__(self):
        self._S = deque()
        self._S_set = set()
        self._R = set()
        self._times = dict()
        self._nodes = dict()

    def addClique(self, c):
        """ Adds a clique to S,
        checking beforehand that this clique is not already present in S. """
        if c not in self._S_set:
            self._S.appendleft(c)
            #self._S.append(c)
            self._S_set.add(c)

    def getClique(self):
        c = self._S.pop()
        # sys.stderr.write("\nGetting clique " + str(c) + "\n")
        return c

    def getDeltaCliques(self, delta):
        """ Returns a set of maximal cliques. """
        iternum = 0
        maxsize = 0
        maxdur = 0

        while len(self._S) != 0:
            iternum += 1
            # sys.stderr.write("S:" + str(len(self._S)) + "\n")
            # sys.stderr.write("T " + str(iternum) + " " + str(len(self._R)) + "\n")
            c = self.getClique()
            is_max = True

            # Grow time on the right side
            td = c.getTd(self._times, delta)
            if c._te != td + delta:
                c_add = Clique((c._X, (c._tb, td + delta)), c._candidates)
                self.addClique(c_add)
                # sys.stderr.write(
                #     "Adding " +
                #     str(c_add) +
                #     " (time delta extension)\n")
                is_max = False
            # else:
            #     sys.stderr.write(str(c) + " cannot grow on the right side\n")

            # Grow time on the left side
            tp = c.getTp(self._times, delta)
            if c._tb != tp - delta:
                c_add = Clique((c._X, (tp - delta, c._te)), c._candidates)
                self.addClique(c_add)
                # sys.stderr.write(
                #     "Adding " +
                #     str(c_add) +
                #     " (left time delta extension)\n")
                is_max = False
            # else:
            #     sys.stderr.write(str(c) + " cannot grow on the left side\n")

            # Grow node set
            candidates = c.getAdjacentNodes(self._times, self._nodes, delta)
            # sys.stderr.write("    Candidates : %s.\n" % (str(candidates)))

            for node in candidates:
                if c.isClique(self._times, node, delta):
                    Xnew = set(c._X).union([node])
                    # sys.stderr.write(str(candidates) +
                    #                  " VS " +
                    #                  str(c._candidates) +
                    #                  "\n")
                    c_add = Clique(
                        (frozenset(Xnew), (c._tb, c._te)), c._candidates)
                    self.addClique(c_add)
                    # sys.stderr.write(
                    #     "Adding " +
                    #     str(c_add) +
                    #     " (node extension)\n")
                    is_max = False

            if is_max:
                # sys.stderr.write(str(c) + " is maximal\n")
                maxsize = max(maxsize, len(c._X))
                maxdur = max(maxdur, c._te - c._tb)
                # sys.stderr.write("M " + str(iternum) + " " + str(maxsize) + " " + str(maxdur) + "\n")
                self._R.add(c)
        return self._R

    ##############################################################
    # Updated by [Boekhout, 2024] to write cliques to file
    ##############################################################
    def printCliques(self, outputfile):
        with open(outputfile, 'w') as out:
            for c in list(self._R):
                out.write(str(c) + "\n")
    ##############################################################

    def __str__(self):
        msg = ""
        for c in self._R:
            msg += str(c) + "\n"
        return msg

    ##############################################################
    # Added by [Boekhout, 2024] for post-processing
    ##############################################################
    def checkSubclique(self, c, max_mem_size, border_reduc_R, index_dict):
        c_mem_size = len(c._X)

        for o_mem_size in range(c_mem_size+1, max_mem_size+1):
            # Determine all indices with at least one overlap member
            all_larger_indices = set()
            for c_member in list(c._X):
                all_larger_indices.update(index_dict[o_mem_size][c_member])
            # Loop over all such indices to determine larger cliques that fully overlap clique c
            for o_ind in sorted(list(all_larger_indices)):
                other = border_reduc_R[o_ind]
                if len(set(c._X) - set(other._X)) == 0:
                    # Check if c is also temporally dominated by other
                    if other._tb <= c._tb and c._te <= other._te:
                        return False
        return True

    def postProcess(self):
        if len(self._R) == 0:
            return
        # First we update the borders to their borders according to the Boekhout & Takes definition
        old_R = list(self._R)
        border_reduc_R = []
        index_dict = defaultdict(lambda: defaultdict(set))
        cur_ind = 0
        self._R.clear()
        for c in old_R:
            c.setTrueBorders(self._times)
            border_reduc_R.append(c)
            for member in list(c._X):
                index_dict[len(c._X)][member].add(cur_ind)
            cur_ind += 1

        # Then we determine for each clique if it has remained maximal
        max_mem_size = max(index_dict.keys())
        for c_ind in range(len(border_reduc_R)):
            c = border_reduc_R[c_ind]
            if self.checkSubclique(c, max_mem_size, border_reduc_R, index_dict):
                self._R.add(c)
    ##############################################################
