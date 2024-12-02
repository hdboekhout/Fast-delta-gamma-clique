'''
    Temporal cliques: Enumerating delta-cliques in temporal graphs. 
    Copyright (C) 2016 Anne-Sophie Himmel
    For licensing see COPYING.
'''

class DeltaInterval:

    def __init__(self, clique, d):
        (v,(s,e)) = clique
        self.vertex = v
        self.startTime = s
        self.finishTime = e
        self.dismissElements = d

    def __str__(self):
        return "("+ str(self.vertex) + "," + str(self.startTime) + "," + str(self.finishTime)+")) - "+str(len(self.dismissElements))
