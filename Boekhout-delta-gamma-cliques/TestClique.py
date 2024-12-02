"""
  The test cases included in this file are primarily intended to test the correctness
  of the stretching phase. The bulking phase edge cases are extremely complex and do
  not translate easily to a toy example and are currently considered future work.
"""

import unittest
from CliqueMaster import CliqueMaster
from Clique import Clique
from collections import deque
import sys
import os

class TestClique(unittest.TestCase):

  def setUp(self):
    self.Cm = CliqueMaster(False)
    sys.stderr = open(os.devnull, 'w')
    self._test_file = "temp.txt"

  def unweightedTest(self, link_stream, delta, gamma, R_expected):
    # Prepare a link stream file and read it in
    with open(self._test_file, 'w') as out:
      for link in link_stream:
        out.write("{} {} {}\n".format(link[0], link[1], link[2]))
    self.Cm.readLinkStream(self._test_file, " ")
    #print("\n===========\ntimes: {}\nweights: {}\nnodes: {}\n-----------".format(self.Cm._times, self.Cm._weights, self.Cm._nodes))
    # Enumerate delta gamma cliques (for specific delta and gamma)
    self.Cm.enumerateDeltaGammaCliques(delta, gamma)
    #print("===========")
    # Compare to expected results
    debug_msg = "\nGot :\n" + str(self.Cm)
    debug_msg += "\nExpected :\n"
    for c in R_expected:
        debug_msg += str(c) + "\n"
    self.assertEqual(self.Cm._R, R_expected, debug_msg)
    # Remove test file
    try:
      os.remove(self._test_file)
    except:
      pass

  def weightedTest(self, link_stream, delta, gamma, R_expected):
    # Prepare a link stream file and read it in
    with open(self._test_file, 'w') as out:
      for link in link_stream:
        out.write("{} {} {} {}\n".format(link[0], link[1], link[2], link[3]))
    self.Cm.readLinkStream(self._test_file, " ", weighted=True)
    #print("\n===========\ntimes: {}\nweights: {}\nnodes: {}\n-----------".format(self.Cm._times, self.Cm._weights, self.Cm._nodes))
    # Enumerate delta gamma cliques (for specific delta and gamma)
    self.Cm.enumerateDeltaGammaCliques(delta, gamma)
    #print("===========")
    # Compare to expected results
    debug_msg = "\nGot :\n" + str(self.Cm)
    debug_msg += "\nExpected :\n"
    for c in R_expected:
        debug_msg += str(c) + "\n"
    self.assertEqual(self.Cm._R, R_expected, debug_msg)
    # Remove test file
    try:
      os.remove(self._test_file)
    except:
      pass


  def test_1_1_unweighted(self):
    # Prepare link stream and expected cliques
    link_stream = [(1, 1, 2), (2, 1, 2),
                   (2, 2, 3), (4, 2, 3),
                   (1, 1, 3), (2, 1, 3), (3, 1, 3), (4, 1, 3)]
    R_expected = set([
        Clique((frozenset([1, 2, 3]), (2, 2))),
        Clique((frozenset([1, 2]), (1, 2))),
        Clique((frozenset([2, 3]), (4, 4))),
        Clique((frozenset([1, 3]), (1, 4)))
    ])
    # Run test
    self.unweightedTest(link_stream, 1, 1, R_expected)

  def test_3_2_unweighted(self):
    # Prepare link stream and expected cliques
    link_stream = [(1, 1, 2), (2, 1, 2),
                   (2, 2, 3), (3, 2, 3),
                   (1, 1, 3), (2, 1, 3), (3, 1, 3), (4, 1, 3)]
    R_expected = set([
        Clique((frozenset([1, 2, 3]), (1, 3))),
        Clique((frozenset([1, 3]), (1, 4)))
    ])
    # Run test
    self.unweightedTest(link_stream, 3, 2, R_expected)

  def test_multiple_link_overlaps(self):
    # Prepare link stream and expected cliques
    link_stream = [(1, 1, 2), (2, 1, 2), (5, 1, 2), (6, 1, 2),
                   (2, 2, 3), (3, 2, 3), (5, 2, 3), (6, 2, 3),
                   (1, 1, 3), (2, 1, 3), (3, 1, 3), (4, 1, 3), (5, 1, 3)]
    R_expected = set([
        Clique((frozenset([1, 2, 3]), (1, 3))),
        Clique((frozenset([1, 2, 3]), (4, 6))),
        Clique((frozenset([2, 3]), (2, 6))),
        Clique((frozenset([1, 3]), (1, 5)))
    ])

    # Run test
    self.unweightedTest(link_stream, 3, 2, R_expected)

  def test_mismatched_overlap(self):
    # Prepare link stream and expected cliques

    # delta = 3, gamma = 2 solution
    link_stream = [(1, 1, 2), (2, 1, 2),
                   (2, 2, 3), (4, 2, 3),
                   (1, 1, 3), (2, 1, 3), (3, 1, 3), (4, 1, 3)]
    R_expected = set([
        Clique((frozenset([1, 2]), (1, 2))),
        Clique((frozenset([2, 3]), (2, 4))),
        Clique((frozenset([1, 3]), (1, 4)))
    ])

    # Run test
    self.unweightedTest(link_stream, 3, 2, R_expected)

  def test_3_2_unweighted_stretch_full(self):
    # Prepare link stream and expected cliques
    link_stream = [(1, 1, 2), (2, 1, 2),
                   (4, 1, 2), (5, 1, 2),
                   (6, 1, 2), (7, 1, 2), (9, 1, 2)]
    R_expected = set([
        Clique((frozenset([1, 2]), (1, 9)))
    ])
    # Run test
    self.unweightedTest(link_stream, 3, 2, R_expected)

  def test_3_2_unweighted_stretch_parts(self):
    # Prepare link stream and expected cliques
    link_stream = [(1, 1, 2), (2, 1, 2),
                   (6, 1, 2), (7, 1, 2), (9, 1, 2)]
    R_expected = set([
        Clique((frozenset([1, 2]), (1, 2))),
        Clique((frozenset([1, 2]), (6, 9)))
    ])
    # Run test
    self.unweightedTest(link_stream, 3, 2, R_expected)

  def test_3_2_unweighted_stretch_failing_delta(self):
    # Prepare link stream and expected cliques
    link_stream = [(1, 1, 2), (2, 1, 2),
                   (4, 1, 2),
                   (6, 1, 2), (7, 1, 2), (9, 1, 2)]
    R_expected = set([
        Clique((frozenset([1, 2]), (1, 4))),
        Clique((frozenset([1, 2]), (4, 9)))
    ])
    # Run test
    self.unweightedTest(link_stream, 3, 2, R_expected)

  def test_bulk_init_overlap_output(self):
    # Prepare link stream and expected cliques
    link_stream = [(1, 1, 2), (2, 1, 2), (5, 1, 2), (6, 1, 2), (7, 1, 2),
                   (6, 2, 3), (7, 2, 3), (8, 2, 3), (10, 2, 3),
                   (6, 1, 3), (7, 1, 3), (8, 1, 3), (10, 1, 3)]
    R_expected = set([
        Clique((frozenset([1, 2]), (1, 7))),
        Clique((frozenset([1, 3]), (6, 10))),
        Clique((frozenset([2, 3]), (6, 10))),
        Clique((frozenset([1, 2, 3]), (5, 8)))
    ])
    # Run test
    self.unweightedTest(link_stream, 4, 2, R_expected)

  def test_3_2_unweighted_larger(self):
    # Prepare link stream and expected cliques
    link_stream = [(1, 1, 2), (2, 1, 2),
                   (2, 2, 3), (3, 2, 3),
                   (1, 1, 3), (2, 1, 3), (3, 1, 3), (4, 1, 3),
                   (2, 1, 4), (3, 1, 4),
                   (2, 2, 4), (3, 2, 4),
                   (2, 3, 4), (3, 3, 4),
                   (2, 4, 5), (3, 4, 5),]
    R_expected = set([
        Clique((frozenset([1, 2, 3, 4]), (1, 3))),
        Clique((frozenset([1, 3, 4]), (1, 4))),
        Clique((frozenset([4, 5]), (2, 3)))
    ])
    # Run test
    self.unweightedTest(link_stream, 3, 2, R_expected)

  def test_3_2_weighted_larger(self):
    # Prepare link stream and expected cliques
    link_stream = [(1, 1, 2, 2), (2, 1, 2, 2),
                   (2, 2, 3, 2), (3, 2, 3, 2),
                   (1, 1, 3, 2), (2, 1, 3, 2), (3, 1, 3, 2), (4, 1, 3, 2),
                   (2, 1, 4, 2), (3, 1, 4, 2),
                   (2, 2, 4, 2), (3, 2, 4, 2),
                   (2, 3, 4, 2), (3, 3, 4, 2),
                   (2, 4, 5, 2), (3, 4, 5, 2),]
    R_expected = set([
        Clique((frozenset([1, 2, 3, 4]), (1, 4))),
        Clique((frozenset([4, 5]), (2, 3)))
    ])
    # Run test
    self.weightedTest(link_stream, 3, 2, R_expected)

  def test_5_3_weighted_stretch_no_yesatend(self):
    # Prepare link stream and expected cliques
    link_stream = [(2010, 1, 2, 1), (2014, 1, 2, 1), (2016, 1, 2, 1), (2018, 1, 2, 1)]
    R_expected = set([
        Clique((frozenset([1, 2]), (2014, 2018)))
    ])
    # Run test
    self.weightedTest(link_stream, 5, 3, R_expected)

  def test_5_3_weighted_stretch_yesexceedsdelta_yesatend(self):
    # Prepare link stream and expected cliques
    link_stream = [(2010, 1, 2, 2), (2014, 1, 2, 1), (2016, 1, 2, 1), (2018, 1, 2, 1)]
    R_expected = set([
        Clique((frozenset([1, 2]), (2010, 2014))),
        Clique((frozenset([1, 2]), (2014, 2018)))
    ])
    # Run test
    self.weightedTest(link_stream, 5, 3, R_expected)

  def test_5_4_weighted_stretch_yesexceedsdelta_no_yesatend(self):
    # Prepare link stream and expected cliques
    link_stream = [(2010, 1, 2, 2), (2011, 1, 2, 1), (2014, 1, 2, 1), (2015, 1, 2, 1), (2018, 1, 2, 2)]
    R_expected = set([
        Clique((frozenset([1, 2]), (2010, 2014))),
        Clique((frozenset([1, 2]), (2014, 2018)))
    ])
    # Run test
    self.weightedTest(link_stream, 5, 4, R_expected)

  def test_5_4_weighted_stretch_yesexceedsdelta_no(self):
    # Prepare link stream and expected cliques
    link_stream = [(2010, 1, 2, 2), (2011, 1, 2, 1), (2014, 1, 2, 1), (2015, 1, 2, 1), (2018, 1, 2, 1)]
    R_expected = set([
        Clique((frozenset([1, 2]), (2010, 2014)))
    ])
    # Run test
    self.weightedTest(link_stream, 5, 4, R_expected)

  def test_5_4_weighted_stretch_yesexceedsdeltaaftergrowth_no(self):
    # Prepare link stream and expected cliques
    link_stream = [(2010, 1, 2, 2), (2011, 1, 2, 2), (2014, 1, 2, 1), (2015, 1, 2, 1), (2018, 1, 2, 1)]
    R_expected = set([
        Clique((frozenset([1, 2]), (2010, 2015)))
    ])
    # Run test
    self.weightedTest(link_stream, 5, 4, R_expected)

  def test_5_4_weighted_stretch_no(self):
    # Prepare link stream and expected cliques
    link_stream = [(2010, 1, 2, 2), (2011, 1, 2, 1), (2015, 1, 2, 1), (2018, 1, 2, 1)]
    R_expected = set()
    # Run test
    self.weightedTest(link_stream, 5, 4, R_expected)

  def test_5_4_weighted_stretch_yesatendaftergrowth(self):
    # Prepare link stream and expected cliques
    link_stream = [(2010, 1, 2, 2), (2011, 1, 2, 1), (2014, 1, 2, 2), (2015, 1, 2, 2), (2018, 1, 2, 1)]
    R_expected = set([
        Clique((frozenset([1, 2]), (2010, 2018)))
    ])
    # Run test
    self.weightedTest(link_stream, 5, 4, R_expected)

if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestClique)
  unittest.TextTestRunner(verbosity=2).run(suite)