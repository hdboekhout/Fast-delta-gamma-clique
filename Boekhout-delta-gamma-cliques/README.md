# Fast maximal ($\delta,\gamma$)-clique enumeration

Algorithm for enumerating ($\delta,\gamma$)-maximal cliques from a linkstream dataset.
This method was introduced in the following paper.

```
Fast maximal clique enumeration in weighted temporal networks. Hanjo D. Boekhout and Frank W. Takes, to appear.

```

Please cite the above paper when using this code.

## Usage

```
python3 main.py -in <data_file> -out <output_directory> -d <int:delta> -g <float:gamma> -v <bool:verbose> -w <bool:weighted>
```
Note that: the verbose and weighted arguments are optional; the **delta and gamma variables must be positive** (i.e., $\geq 0$); and that the verbose parameter determines whether progress is reported during the bulking phase of the algorithm or not.

The data_file should be formatted as a temporally ordered sequence of quadruplets ($t,u,v,w$) describing an edge between vertex $u$ and $v$ at timestamp $t$ with weight $w$.
For example:

```
1 2 3 1
1 4 3 -1
2 2 3 1
...
```
means that at timestamp 1 nodes 2 and 3 are connected with a weight of 1; and nodes 4 and 3 with a weight of -1. Note that if weighted is False triplets may be used. Furthermore, note that weights may be negative.

The code can be run on test cases by using
```
python3 TestClique.py
```

The code was last tested using Python 3.12.3.
