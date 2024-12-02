# -*-coding:utf8*-
import sys
from collections import deque
from Clique_m import Clique
import networkx as nx
import itertools
import pandas as pd
#from itertools import combinations
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
from collections import defaultdict

class CliqueMaster:

    def __init__(self):
        self._S = deque()
        self._S_set = set()
        self._R = set()
        self._times = dict()
        self._nodes = dict()
        self._graph = nx.Graph()
        self._clique_dict = dict()
        self._result_list = []
        self._iternum = 0
        #self._maxsize = 0
        #self._maxdur = 0

    def addClique(self, c):
        """ Adds a clique to S,
        checking beforehand that this clique is not already present in S. """
        if c not in self._S_set:
            self._S.appendleft(c)
            #self._S.append(c)
            self._S_set.add(c)

    def getClique(self):
        c = self._S.pop()
        #sys.stderr.write("\nGetting clique " + str(c) + "\n")  #### ----------------- print removed 12122019
        return c

    def getDeltaCliques(self, delta):
        """ Returns a set of maximal cliques. """
        iternum = 0
        maxsize = 0
        maxdur = 0

        while len(self._S) != 0:
            iternum += 1
            #sys.stderr.write("S:" + str(len(self._S)) + "\n")                         #### ----------------- print removed 12122019
            #sys.stderr.write("T " + str(iternum) + " " + str(len(self._R)) + "\n")    #### ----------------- print removed 12122019
            c = self.getClique()
            is_max = True

            # Grow time on the right side
            td = c.getTd(self._times, delta)
            if c._te != td + delta:
                c_add = Clique((c._X, (c._tb, td + delta)), c._candidates)
                self.addClique(c_add)
                #sys.stderr.write("Adding " + str(c_add) + " (time delta extension)\n")   #### ----------------- print removed 12122019
                is_max = False
            else:
                pass
                #sys.stderr.write(str(c) + " cannot grow on the right side\n")           #### ----------------- print removed 12122019

            # Grow time on the left side
            tp = c.getTp(self._times, delta)
            if c._tb != tp - delta:
                c_add = Clique((c._X, (tp - delta, c._te)), c._candidates)
                self.addClique(c_add)
                #sys.stderr.write("Adding " + str(c_add) + " (left time delta extension)\n")   #### ----------------- print removed 12122019
                is_max = False
            else:
                pass
                #sys.stderr.write(str(c) + " cannot grow on the left side\n")   #### ----------------- print removed 12122019

            # Grow node set
            candidates = c.getAdjacentNodes(self._times, self._nodes, delta)
            #sys.stderr.write("    Candidates : %s.\n" % (str(candidates)))  #### ----------------- print removed 12122019

            for node in candidates:
                if c.isClique(self._times, node, delta):
                    Xnew = set(c._X).union([node])
                    #sys.stderr.write(str(candidates) + " VS " + str(c._candidates) + "\n")  #### ----------------- print removed 12122019
                    c_add = Clique(
                        (frozenset(Xnew), (c._tb, c._te)), c._candidates)
                    self.addClique(c_add)
                    #sys.stderr.write( "Adding " + str(c_add) + " (node extension)\n")   #### ----------------- print removed 12122019
                    is_max = False

            if is_max:
                #sys.stderr.write(str(c) + " is maximal\n")   #### ----------------- print removed 12122019
                maxsize = max(maxsize, len(c._X))
                maxdur = max(maxdur, c._te - c._tb)
                #sys.stderr.write("M " + str(iternum) + " " + str(maxsize) + " " + str(maxdur) + "\n")  #### ----------------- print removed 12122019
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


#### Bithika:
    def printInitialCliques(self):
        for c in self._S:
            #sys.stdout.write(str(c) + ' neighbor candidates:' + str(c._candidates) + "\n")
            sys.stdout.write(str(c) + "\n")
            #self._result_list.append([list(c._X), len(c._X), c._tb, c._te, c._te - c._tb])  ### initial clique test
        print(self._clique_dict)

#### Bithika:
    def printCliquesDistribution(self, delta):
        Maximal_Clique_df = pd.DataFrame(self._result_list, columns=['node_set', 'cardinality', 'tb', 'te', 'duration'])
        Maximal_Clique_df = Maximal_Clique_df[['cardinality','duration']]
        Maximal_Clique_df = Maximal_Clique_df.astype(int) 
        Maximal_Clique_df = Maximal_Clique_df[ ~((Maximal_Clique_df['duration'] == 2*delta) & (Maximal_Clique_df['cardinality'] == 2))]       
        Maximal_Cardinality_df = Maximal_Clique_df.groupby(['cardinality'], sort=True).size().reset_index(name='counts')
        Maximal_Duration_df = Maximal_Clique_df.groupby(['duration'], sort=True).size().reset_index(name='counts')
        Maximal_df = Maximal_Clique_df.groupby(['cardinality','duration'], sort=True).size().reset_index(name='counts')
        print("Maximal cardinality DF:")
        print(Maximal_Cardinality_df)
        print("Maximal duration DF:")
        print(Maximal_Duration_df)
        print("Maximal DF:")
        print(Maximal_df)
        plt.bar(Maximal_Cardinality_df['cardinality'], Maximal_Cardinality_df['counts'])
        #plt.ylim(0,700)
        plt.xlabel('Cardinality')
        plt.ylabel('Count')
        plt.title('Frequency Distribution of Maximal Cardinality')
        plt.show()
        plt.plot(Maximal_Duration_df['duration'], Maximal_Duration_df['counts'])
        #plt.ylim(0,20)
        plt.xlabel('Duration')
        plt.ylabel('Count')
        plt.title('Frequency Distribution of Maximal Duration')
        plt.show()
        #Maximal_df = Maximal_df[1:]
        #Maximal_df[['cardinality','counts']].boxplot(by='cardinality')
        #plt.show()
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.scatter( Maximal_df['cardinality'], Maximal_df['duration'], Maximal_df['counts'], c=Maximal_df['counts'])
        ax.set_title('Detailed View on #Maximal Cliques')
        ax.set_xlabel('Cardinality')
        ax.set_ylabel('Duration')
        ax.set_zlabel('Count')
        plt.show()


#### Bithika:
    def getDeltaGammaCliques(self, delta, gamma):
        NOT_MAXIMAL = True
        maxsize = 0
        maxdur = 0
        iternum = 0
        while(NOT_MAXIMAL):
            T = deque()
            while(len(self._S) != 0):
                iternum += 1
                c = self.getClique()
                is_max = True
                candidates = c._candidates
                for node in candidates:
                    xn = [ h for h in c._X]
                    xn.append(node)
                    X_new = c._X.union([node])
                    if frozenset(X_new) in self._clique_dict :
                        if (c._tb, c._te) in self._clique_dict[frozenset(X_new)]:
                            is_max = False
                    else:
                        check_flag, temp_ts = self.checkClique(node, frozenset(c._X))  ##_with2
                        if check_flag:
                            neighbors_node = self._graph.neighbors(node)
                            neighborlist = candidates.intersection(neighbors_node).difference(X_new) #difference(node)
                            for element in itertools.product(*temp_ts):
                                max_tb = []
                                min_te = []
                                for e in element:
                                    max_tb.append(e[0])
                                    min_te.append(e[1])
                                tb = max(max_tb)
                                te = min(min_te)
                                if (te -tb) >= delta : 
                                    c_add = Clique((frozenset(X_new), (tb, te)), neighborlist)
                                    T.appendleft(c_add)
                                    if frozenset(xn) in self._clique_dict:
                                        self._clique_dict[frozenset(X_new)].append((tb,te))
                                    else:
                                        self._clique_dict[frozenset(X_new)] = []
                                        self._clique_dict[frozenset(X_new)].append((tb,te))
                                    
                                    if tb == c._tb and te == c._te:
                                        is_max = False



                if is_max:
                    #sys.stderr.write(str(c) + " is maximal\n") #### ----------------- print removed 12122019
                    #maxsize = max(maxsize, len(c._X))
                    #maxdur = max(maxdur, c._te - c._tb)
                    #sys.stderr.write("M " + str(iternum) + " " + str(maxsize) + " " + str(maxdur) + "\n")  #### ----------------- print removed 12122019
                    self._iternum = iternum
                    #self._maxsize = maxsize
                    #self._maxdur = maxdur
                    self._result_list.append([list(c._X), len(c._X), c._tb, c._te, c._te - c._tb])
                    self._R.add(c)

  
            if len(T) > 0: 
                for t in T:
                    self.addClique(t)
            else:
                NOT_MAXIMAL = False

        return self._R


#### Bithika:
    def checkClique(self, node, X):
        temp_ts = []
        temp_ts.append(self._clique_dict[X])
        for u in X:
            Z=set(X)-set([u])
            Z_new=Z.union([node])
            Y = frozenset(Z_new)
            #l=[i for i in Z]
            #l.append(node)
            #Y = frozenset(l)
            #Y = frozenset([u, node])
            if Y not in self._clique_dict:
                return (False, 0)
            else:
                temp_ts.append(self._clique_dict[Y])
        return (True, temp_ts)

#### Bithika:
    def checkClique_with2(self, node, X):
        temp_ts = []
        X_new = list(X)
        X_new.append(node)
        comb = itertools.combinations(X_new, 2)
        for u in comb:
            Y = frozenset([u[0], u[1]])
            #l=[i for i in Z]
            #l.append(node)
            #Y = frozenset(l)
            #Y = frozenset([u, node])
            if Y not in self._clique_dict:
                return (False, 0)
            else:
                temp_ts.append(self._clique_dict[Y])
        return (True, temp_ts)

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
            # Loop over all such indices to determine parent/child relation and sibling relations to larger cliques
            for o_ind in sorted(list(all_larger_indices)):
                other = border_reduc_R[o_ind]
                if len(set(c._X) - set(other._X)) == 0:
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


