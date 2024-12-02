'''
    Temporal cliques: Enumerating delta-cliques in temporal graphs. 
    Copyright (C) 2016 Anne-Sophie Himmel
    For licensing see COPYING.
'''

import sys
import bisect
import collections
from Neighborhood import Neighborhood

def pivotingOne(pivots, pivotIntervals):
    _, dismissElements = pivots.popitem()
    print("# dismissed elements: " + str(len(dismissElements)))
    return dismissElements

def pivotingOneMax(pivots, pivotIntervals):
    maxValue = 0
    maxElement = 0
    dismissElements = set()
    for el in pivots:
        l = len(pivots[el])
        if l  > maxValue:
            maxValue = l
            maxElement = el
    if maxValue > 0:
        dismissElements = pivots[maxElement]
        print("# dismissed elements: " + str(len(dismissElements)))
    return dismissElements

def pivotingMany(pivots, pivotIntervals):
    pivot_elements = []

    dismissElements = set()
    n_chosen = 0

    # Gather non-overlapping pivots.  This is a very slow
    # implementation and should be much faster if we would look at
    # the intervals in order.
    while len(pivots) > 0:
        act_el, new_dismiss_elements = pivots.popitem()

        _, (ae_s, ae_e) = act_el

        eligible = True

        for piv_el in pivot_elements:
            _, (pe_s, pe_e) = piv_el
            a = max(ae_s, pe_s)
            b = min(ae_e, pe_e)
            if a <= b:
                eligible = False
                break

        if eligible:
            pivot_elements.append(act_el)
            dismissElements = dismissElements.union(new_dismiss_elements)
            n_chosen += 1

    print("# pivots: " + str(n_chosen))
    print("# dismissed elements: " + str(len(dismissElements)))
    return dismissElements

def find_max_el(pivots, pivotIntervals):
    maxValue = 0
    maxElement = 0
    dismissElements = set()
    for el in pivots:
        l = len(pivots[el])
        if l  > maxValue:
            maxValue = l
            maxElement = el

    dismissElements = pivots[maxElement]

    return maxElement, dismissElements

def pivotingGreedy(pivots, pivotIntervals):
    pivot_elements = []
    dismiss_el = set()
    n_chosen = 0

    while len(pivots) > 0:
        max_el, new_dismiss_el = find_max_el(pivots, pivotIntervals)
        n_chosen += 1

        dismiss_el = dismiss_el.union(new_dismiss_el)

        _, (me_s, me_e) = max_el

        rem_pivots = []
        for piv_el in pivots:
            _, (pe_s, pe_e) = piv_el
            a = max(me_s, pe_s)
            b = min(me_e, pe_e)
            if a <= b:
                rem_pivots = rem_pivots + [piv_el]

        for re in rem_pivots:
            pivots.pop(re)

    print("# pivots: " + str(n_chosen))
    print("# dismissed elements: " + str(len(dismiss_el)))
    return dismiss_el

def pivotingOptimal(pivots, pivotIntervals):
    # Assume: pivots contains at least two elements.

    n_ivals = len(pivotIntervals)

    # First, sort by finish time (breaking ties arbitrarily but
    # consistently), and compute for each interval i the smallest
    # interval with earlier finish time than i's starting time.
    def interval_compare(x, y):
        if x.finishTime == y.finishTime:
            if x.vertex <= y.vertex:
                # This is a comparison of strings.  It
                # cannot happen that they are equal
                # here.
                return -1
            else:
                return 1
        else:
            return x.finishTime - y.finishTime

    pivotIntervals.sort(cmp = interval_compare)

    succinct_start = []

    for i in range(0, n_ivals):
        item = (pivotIntervals[i], i)
        #print str(pivotIntervals[i].startTime) + " " + str(pivotIntervals[i].finishTime) + " " + str(len(pivotIntervals[i].dismissElements))
        succinct_start.append(item)

    succinct_start.sort(key = lambda item: item[0].startTime)

    previous = [-1] * n_ivals
    curr = 0

    # print str(pivotIntervals)
    # print str(succinct_start)
    # print str(pivotIntervals[9])

    for i in range(1, n_ivals):
        while pivotIntervals[curr].finishTime < succinct_start[i][0].startTime:
            # print "I'm doing " + str(i) + " at " + str(curr)
            curr += 1
        if pivotIntervals[curr].startTime == pivotIntervals[curr].finishTime:
            # This is only the case if Delta = 0, which
            # we'll treat in a special way
            previous[succinct_start[i][1]] = curr - 1
        elif pivotIntervals[curr].finishTime > succinct_start[i][0].startTime:
            previous[succinct_start[i][1]] = curr - 1
        else:
            previous[succinct_start[i][1]] = curr
        #print str(curr)
        #print str(succinct_start[i][1]) + ": " + str(previous[succinct_start[i][1]])

    # Second, find the max. number of removed elements by dynamic
    # programming.
    opt = [0] * n_ivals
    opt[0] = len(pivotIntervals[0].dismissElements)
    chosen = [-1] * n_ivals
    chosen[0] = (True, -1)

    for i in range(1, n_ivals):
        n_dismiss = len(pivotIntervals[i].dismissElements)
        if previous[i] < 0:
            if opt[i - 1] <= n_dismiss:
                opt[i] = n_dismiss
                chosen[i] = (True, -1)
            else:
                opt[i] = opt[i - 1]
                chosen[i] = (False, i - 1)
        else:
            if opt[i - 1] <= opt[previous[i]] + n_dismiss:
                opt[i] = opt[previous[i]] + n_dismiss
                chosen[i] = (True, previous[i])
            else:
                opt[i] = opt[i - 1]
                chosen[i] = (False, i - 1)
        #print "I'm trying " + str(i) + ", setting " + str(opt[i]) + ", getting " + str(chosen[i])

    # Finally, construct solution.
    dismiss_elems = set()
    i = n_ivals - 1
    n_chosen = 0

    while i >= 0:
        #print "I'm trying " + str(i) + ", getting " + str(chosen[i])

        ival_chosen, _ = chosen[i]
        if ival_chosen:
            ival = pivotIntervals[i]
            dismiss_elems.update(ival.dismissElements)
            i = previous[i]
            n_chosen += 1
        else:
            i -= 1

    print("# pivots: " + str(n_chosen))
    print("# dismissed elements: " + str(len(dismiss_elems)))
    return dismiss_elems
