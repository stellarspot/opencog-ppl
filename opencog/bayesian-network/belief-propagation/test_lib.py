from opencog.type_constructors import *


def get_value_list(atom, key):
    return atom.get_value(ConceptNode(key)).to_list()


def almost_equal_lists(list1, list2):
    return almost_equal_lists_with_precision(list1, list2, 0.1)


def almost_equal_lists_with_precision(list1, list2, precision):
    delta = 0.0
    for i in range(0, len(list1)):
        delta += abs(list2[i] - list1[i])
    return delta < precision
