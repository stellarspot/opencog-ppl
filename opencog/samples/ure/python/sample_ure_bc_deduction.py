from opencog.ure import BackwardChainer
from opencog.type_constructors import *
from opencog.utilities import initialize_opencog
from opencog.atomspace import TruthValue

# Initialize AtomSpace

atomspace = AtomSpace()
initialize_opencog(atomspace)

# Import URE Deduction Rules
from sample_ure_deduction import *

# Knowledge Base
A = ConceptNode("A")
B = ConceptNode("B")
C = ConceptNode("C")

AB = InheritanceLink(A, B)
BC = InheritanceLink(B, C)

A.tv = TruthValue(1, 1)
AB.tv = TruthValue(0.8, 0.9)
BC.tv = TruthValue(0.85, 0.95)

# Run Forward Chainer

chainer = BackwardChainer(atomspace,
                          deduction_rbs,
                          InheritanceLink(VariableNode("$X"), C),
                          TypedVariableLink(VariableNode("$X"), TypeNode("ConceptNode")))

chainer.do_chain()
results = chainer.get_results()

print(results)
