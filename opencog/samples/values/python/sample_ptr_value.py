from opencog.type_constructors import *
from opencog.utilities import initialize_opencog
from opencog.atomspace import PtrValue

# Initialize AtomSpace
atomspace = AtomSpace()
initialize_opencog(atomspace)

key = ConceptNode("key")
node = ConceptNode("node")

dict = {"one": 1, "two": 2}

node.set_value(key, PtrValue(dict))

print('value:', node.get_value(key).value())
