#! /usr/bin/env python

'''
    Delta-slice degeneracy: Copute the delta-slice degeneracy of a temporal graph.
    Copyright (C) 2016 Manuel Sorge

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import networkx
import optparse

# Compute slice graphs
def slice_graph(G, delta, start):
    S = networkx.Graph()
    S.add_nodes_from(G.nodes())
    for (u,v,d) in G.edges(data='times'):
        times = d['times']
        # Slower:
#        print "intersecting " + str(times) + " with " + str(set(range(start, start + delta + 1)))
        # intersection = times & set(range(start, start + delta + 1))
        # if len(intersection) > 0:
        #     S.add_edge(u,v)

        for t in times:
            if t >= start and t <= start + delta:
                S.add_edge(u,v)
                break
#    print "slice graph edges: " + str(len(S.edges()))
    return S


def main():

    usage = "Usage: cat <stream> | compute_degeneracy.py [options]"
    fmt = optparse.IndentedHelpFormatter(max_help_position=50, width=100)

    parser = optparse.OptionParser(usage=usage, formatter=fmt)
    
    parser.add_option("-d", "--delta", type="int", dest="delta", default=0,
                      help="Delta")
    parser.add_option("-o", "--out-file", metavar="FILE", type="string", dest="clique_file", default=None,
                      help="Output degeneracy into FILE")
    parser.add_option("-n", "--normal", action="store_true", dest="normal",
                      help="Also compute degeneracy of the underlying static graph")

    (options, args) = parser.parse_args()

    delta = options.delta
    
    t_min = float('inf')
    t_max = 0
    times = set()

    G = networkx.Graph()

    # Read stream
    for line in sys.stdin:
        contents = line.split()
        t = int(contents[0])
        u = contents[1].strip()
        v = contents[2].strip()

        if u == v:
            print >> sys.stderr, "Ignoring self-loop " + u + " at " + str(t)
            continue

        if not G.has_node(u): G.add_node(u)
        if not G.has_node(v): G.add_node(v)
        if not G.has_edge(u,v):
            G.add_edge(u,v,times=set([t]))
        else:
            G[u][v]['times'].add(t)
#            print "Added to " + u + " " + v + ", got: " + str(G[u][v]['times'])
            
        times.add(t)
        
        t_min = min(t_min, t)
        t_max = max(t_max, t)

    # Compute delta slice degeneracy
    max_degen = 0
    for t in times:
        if t <= t_max - delta:
            S = slice_graph(G, delta, t)
            core_numbers = networkx.core_number(S).values()
#            print str(core_numbers)
            max_degen = max(max_degen, max(core_numbers))

    degen = 0
    if options.normal:
        S = slice_graph(G, t_max - t_min, t_min)
        core_numbers = networkx.core_number(S).values()
        degen = max(core_numbers)

    output = str(max_degen)
    if options.normal:
        output = output + " " + str(degen)
    print output

if __name__ == "__main__":
    sys.exit(main())
