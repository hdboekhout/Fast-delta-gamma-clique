delta-cliques
=============

Algorithm for computing Delta-cliques in link streams

Usage:
```
python3 main.py -in <data_file> -out <output_directory> -d <int:delta>
```

Where data_file is a sequence of triplets:
```
1 2 3
1 1 3
...
```
 Meaning that at time 1, nodes 2 and 3 interacted, etc.

The code can be run on test cases by using
```
python TestClique.py
```
