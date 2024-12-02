
Delta-Clique Enumeration in Temporal Graphs
-------------------------------------------

This tool enumerates all maximal delta-cliques in a given temporal
graph, as described in the paper

       Enumerating Maximal Cliques in Temporal Graphs, Anne-Sophie
       Himmel, Hendrik Molter, Rolf Niedermeier, and Manuel Sorge, to
       appear.

with added post-processing steps to enumerate only delta-cliques
adhering to the definition of delta-cliques specified in the paper

       Fast maximal clique enumeration in weighted temporal networks,
       Hanjo Boekhout and Frank Takes, to appear.

If you use this code in scientific research, please cite the above
articles.

The original version of this tool can be obtained from

    http://fpt.akt.tu-berlin.de/temporalcliques/ .

The tool is distributed under the terms of the GNU General Public
License (GPL, see COPYING).

The modified tool is written in Python 3. To run it, type

    python3 temporal-cliques.py -in <data_file> -out <output_directory> -d <int:delta>

Herein, data_file is a file containing a temporal graph (a
multigraph with integer edge labels) encoded in lines of the form

     t u v

describing an edge between vertex u and vertex v at time step t.
Vertex names can be arbitrary strings but the time step t has to be an
integer. Such temporal graphs can be obtained, for example, from
sociopatterns.org. Other than the data_file an output_directory and
delta, you can further specify a pivoting level using "-p <int:pivot_lvl>"

compute-degeneracy.py is a tool to compute the delta-slice degeneracy
of a temporal graph as defined in the paper cited above.

Original by:
-- Manuel Sorge
   12th May 2016

Updated by:
-- Hanjo Boekhout
   2nd Dec 2024

