"""
MIT License

Copyright (c) 2024 Hanjo Boekhout

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
"""

class CustomNodeLabelling:

  def __init__(self):
    self._nodelabels = dict()

  def createNodeLabelling(self, nodes):
    sorted_nodes = sorted(nodes, key=lambda key: len(nodes[key]))
    current_max_label = 0
    for node in sorted_nodes:
      self._nodelabels[node] = current_max_label
      current_max_label += 1

  def get(self, node):
    return self._nodelabels[node]

  def getSortedNodesByLabel(self, nodelist):
    return sorted(nodelist, key=lambda x: self._nodelabels[x])

  def maxLabelledNode(self, nodeset):
    return max(list(nodeset), key=lambda x: self._nodelabels[x])