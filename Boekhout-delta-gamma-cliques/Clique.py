"""
MIT License

Copyright (c) 2024 Hanjo Boekhout

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
"""

import bisect
import itertools as it

class Clique:

  def __init__(self, c, borders=None, shared_neighbors=None, latest=None):
    (X, (tb, te)) = c
    self._X = X
    self._tb = tb
    self._te = te

    if latest is None:
      self._latestX = max(self._X)
    else:
      self._latestX = latest

    if borders:
      (self._tbMin, self._tbMax, self._teMin, self._teMax) = borders
    else:
      self._tbMin = tb
      self._tbMax = tb
      self._teMin = te
      self._teMax = te

    if shared_neighbors:
      self._shared_neighbors = shared_neighbors
    else:
      self._shared_neighbors = set()


  def __eq__(self, other):
    if self._X == other._X and self._tb == other._tb and self._te == other._te:
      return True
    else:
      return False

  def __hash__(self):
    return hash((self._X, self._tb, self._te))

  def __str__(self):
    return ','.join(map(str, list(self._X))) + " " + \
      str(self._tb) + "," + str(self._te)  + " | "  +str(self._tbMin)+","+str(self._tbMax)+","+str(self._teMin)+","+ str(self._teMax)


  def setSharedNeighbors(self, nodes):
    members = list(self._X)
    self._shared_neighbors = nodes[members[0]]
    for member in members[1:]:
      self._shared_neighbors = self._shared_neighbors.intersection(nodes[member])

  def isTemporallyDominated(self, tb, te):
    if tb <= self._tb and te >= self._te:
      return True
    return False

  def isSpatialGrowthDominated(self, covered_list, nodeLabelling):
    if len([x for x in (self._shared_neighbors - set(covered_list)) if nodeLabelling.get(x) > nodeLabelling.get(self._latestX)]) == 0:
      return True
    return False

  def isSpatialGrowthReachable(self, E_max_tbMin, E_min_teMax):
    if E_max_tbMin <= self._teMin and self._tbMax <= E_min_teMax:
      return True
    return False


  def getMinimumTbFromBorderFull(self, times, left_border, right_border):
    if left_border == right_border:
      return left_border
    link_tbs = [right_border]
    node_combs = [frozenset([u, v]) for (u,v) in it.combinations(self._X, 2)]
    for link in node_combs:
      link_tb = times[link][bisect.bisect_left(times[link], left_border):][0]
      if link_tb == left_border:
        return link_tb
      link_tbs.append(link_tb)
    return min(link_tbs)

  def getMaximumTeToBorderFull(self, times, left_border, right_border):
    if left_border == right_border:
      return left_border
    link_tes = [left_border]
    node_combs = [frozenset([u, v]) for (u,v) in it.combinations(self._X, 2)]
    for link in node_combs:
      link_te = times[link][:bisect.bisect_right(times[link], right_border)][-1]
      if link_te == right_border:
        return link_te
      link_tes.append(link_te)
    return max(link_tes)

  def getMinimumTbFromBorderPart(self, times, left_border, right_border):
    if left_border == right_border:
      return left_border
    link_tbs = [right_border]
    node_combs = [frozenset([u, self._latestX]) for u in list(self._X - {self._latestX})]
    for link in node_combs:
      link_tb = times[link][bisect.bisect_left(times[link], left_border):][0]
      if link_tb == left_border:
        return link_tb
      link_tbs.append(link_tb)
    return min(link_tbs)

  def getMaximumTeToBorderPart(self, times, left_border, right_border):
    if left_border == right_border:
      return left_border
    link_tes = [left_border]
    node_combs = [frozenset([u, self._latestX]) for u in list(self._X - {self._latestX})]
    for link in node_combs:
      link_te = times[link][:bisect.bisect_right(times[link], right_border)][-1]
      if link_te == right_border:
        return link_te
      link_tes.append(link_te)
    return max(link_tes)


  def getMinimumTbFromBorderComb(self, times, left_border, right_border, other):
    if left_border == right_border:
      return left_border
    link_tbs = [right_border]
    node_combs = [frozenset([u, v]) for (u,v) in it.combinations(self._X, 2)] + [frozenset([u, other._latestX]) for u in list(self._X - {self._latestX})]
    for link in node_combs:
      link_tb = times[link][bisect.bisect_left(times[link], left_border):][0]
      if link_tb == left_border:
        return link_tb
      link_tbs.append(link_tb)
    return min(link_tbs)

  def getMaximumTeToBorderComb(self, times, left_border, right_border, other):
    if left_border == right_border:
      return left_border
    link_tes = [left_border]
    node_combs = [frozenset([u, v]) for (u,v) in it.combinations(self._X, 2)] + [frozenset([u, other._latestX]) for u in list(self._X - {self._latestX})]
    for link in node_combs:
      link_te = times[link][:bisect.bisect_right(times[link], right_border)][-1]
      if link_te == right_border:
        return link_te
      link_tes.append(link_te)
    return max(link_tes)