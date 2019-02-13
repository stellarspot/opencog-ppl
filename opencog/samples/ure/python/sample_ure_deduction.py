from opencog.type_constructors import *
from opencog.utilities import initialize_opencog
from opencog.atomspace import TruthValue
from opencog.bindlink import execute_atom

atomspace = AtomSpace()
initialize_opencog(atomspace)

a = ConceptNode("A")
b = ConceptNode("B")
c = ConceptNode("C")

AB = InheritanceLink(a, b)
BC = InheritanceLink(b, c)

a.tv = TruthValue(1, 1)
AB.tv = TruthValue(0.8, 0.9)
BC.tv = TruthValue(0.85, 0.95)

fc_deduction_rule = BindLink(
    VariableList(
        TypedVariableLink(
            VariableNode('$A'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$B'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$C'),
            TypeNode('ConceptNode'))),
    AndLink(
        InheritanceLink(
            VariableNode('$A'),
            VariableNode('$B')),
        InheritanceLink(
            VariableNode('$B'),
            VariableNode('$C')),
        NotLink(
            EqualLink(
                VariableNode('$A'),
                VariableNode('$C')))),
    ExecutionOutputLink(
        GroundedSchemaNode('py: fc_deduction_formula'),
        ListLink(
            InheritanceLink(
                VariableNode('$A'),
                VariableNode('$C')),
            InheritanceLink(
                VariableNode('$A'),
                VariableNode('$B')),
            InheritanceLink(
                VariableNode('$B'),
                VariableNode('$C')))))


def fc_deduction_formula(AC, AB, BC):
    tv1 = AB.tv
    tv2 = BC.tv

    if tv1.mean > 0.5 and tv2.mean > 0.5 and tv1.confidence > 0.5 and tv2.confidence > 0.5:
        tv = TruthValue(1, 1)
    else:
        tv = TruthValue(0, 0)

    AC.tv = tv
    return AC


res = execute_atom(atomspace, fc_deduction_rule)
print(res)
