from opencog.atomspace import AtomSpace, types

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *

atomspace = AtomSpace()
initialize_opencog(atomspace)

num1 = NumberNode("0.5")
num2 = NumberNode("0.5")


def probability_and(n1, n2):
    p1 = float(n1.name)
    p2 = float(n2.name)
    return NumberNode(str(p1 * p2))

def probability_or(n1, n2):
    p1 = float(n1.name)
    p2 = float(n2.name)
    return NumberNode(str(p1 + p2 - p1 * p2))

print("probability and: ", probability_and(num1, num2))
print("probability or : ", probability_or(num1, num2))