# Maximal ($\delta,\gamma$)-clique enumeration

This repository contains the code used to produce the results presented in:

```
Fast maximal clique enumeration in weighted temporal networks. Hanjo D. Boekhout and Frank W. Takes, to appear.

```

The implementation of the algorithms introduced in the above paper, and instructions on how to run said implementation, can be found in the *Boekhout-delta-gamma-cliques* directory.

## Modified implementations

The remaining directories provide slightly modified versions of algorithms, specifically those introduced in the following publications:

- *Banerjee-Pal-delta-gamma-cliques* was introduced in:
```
@article{banerjee2024two,
  title={A two-phase approach for enumeration of maximal ($\Delta$, $\gamma$)-cliques of a temporal network},
  author={Banerjee, Suman and Pal, Bithika},
  journal={Social Network Analysis and Mining},
  volume={14},
  number={1},
  pages={54},
  year={2024},
  publisher={Springer}
}
```

- *Himmel-et-al-delta-cliques-with-pivots* was introduced in:
```
@article{himmel2017adapting,
  title={Adapting the Bron--Kerbosch algorithm for enumerating maximal cliques in temporal graphs},
  author={Himmel, Anne-Sophie and Molter, Hendrik and Niedermeier, Rolf and Sorge, Manuel},
  journal={Social Network Analysis and Mining},
  volume={7},
  pages={1--16},
  year={2017},
  publisher={Springer}
}
```

- *Viard-et-al-delta-cliques* was introduced in:
```
@article{viard2016computing,
  title={Computing maximal cliques in link streams},
  author={Viard, Tiphaine and Latapy, Matthieu and Magnien, Cl{\'e}mence},
  journal={Theoretical Computer Science},
  volume={609},
  pages={245--252},
  year={2016},
  publisher={Elsevier}
}
```

Modifications were made primarily to add a post-processing step which produces the clique set that adheres to the ($\delta,\gamma$)-clique defined in the publication listed above. Furthermore, modifications were made to unify their usage and to ensure consistent performance logging. An additional minor fix, for cases where the same link occurs multiple times at the same timestamp, was applied to the code in *Banerjee-Pal-delta-gamma-cliques*.

All appropriate licensing information has been included in the respective directories.

Please cite both the paper by Boekhout & Takes and the original paper when using one of the modified code versions.