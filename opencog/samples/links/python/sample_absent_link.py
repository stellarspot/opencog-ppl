from opencog.utilities import initialize_opencog
from opencog.type_constructors import *
from opencog.bindlink import execute_atom

atomspace = AtomSpace()
initialize_opencog(atomspace)

cat = ConceptNode("cat")
stone = ConceptNode("stone")
animal = ConceptNode("animal")

InheritanceLink(cat, animal)

absent_rule = BindLink(
    TypedVariableLink(
        VariableNode("$X"),
        TypeNode("ConceptNode")
    ),
    AndLink(
        AbsentLink(
            InheritanceLink(
                VariableNode("$X"),
                animal
            )
        ),
        PresentLink(
            VariableNode("$X")
        )
    ),
    VariableNode("$X")
)

absent = execute_atom(atomspace, absent_rule)
print(absent)

absent = execute_atom(atomspace, absent_rule)
print(absent)
