# Sample from:
# https://wiki.opencog.org/w/Manipulating_Atoms_in_Python

from opencog.atomspace import AtomSpace, types

a = AtomSpace()
cat = a.add_node(types.ConceptNode, "Cat")
animal = a.add_node(types.ConceptNode, "Animal")
a.add_link(types.InheritanceLink, [cat, animal])

for atom in a:
    print (atom)

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *
from opencog.bindlink import satisfying_set

initialize_opencog(a)

a.clear()

color = ConceptNode("Color")

InheritanceLink(ConceptNode("Red"), color)
InheritanceLink(ConceptNode("Green"), color)
InheritanceLink(ConceptNode("Blue"), color)

# Create a pattern to look for color nodes
varlink = TypedVariableLink(VariableNode("$xcol"), TypeNode("ConceptNode"))
pattern = InheritanceLink(VariableNode("$xcol"), color)
colornodes = GetLink(varlink, pattern)

print(satisfying_set(a, colornodes))
