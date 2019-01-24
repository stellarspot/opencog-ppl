from opencog.atomspace import AtomSpace, types, TruthValue

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *

# Initialization
atomspace = AtomSpace()
initialize_opencog(atomspace)

# Counter
counter = 0

def get_counter():
    global counter
    counter = counter + 1
    return NumberNode(str(counter))


print("counter: ", get_counter())
print("counter: ", get_counter())

# Factor

def get_factor(variables):
    names = list(map(lambda node: node.name, variables.out))
    print(names)
    names.sort()
    name = '-'.join(names)
    return ConceptNode('Factor-' + name)

print("factor: ", get_factor(ListLink(ConceptNode("A"))))
print("factor: ", get_factor(ListLink(ConceptNode("A"), ConceptNode("B"))))
