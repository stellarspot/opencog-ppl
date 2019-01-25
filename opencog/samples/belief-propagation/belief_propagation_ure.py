from opencog.atomspace import AtomSpace, types, TruthValue

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *
from opencog.bindlink import bindlink

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
    names.sort()
    name = '-'.join(names)
    return ConceptNode('Factor-' + name)

print("factor: ", get_factor(ListLink(ConceptNode("A"))))
print("factor: ", get_factor(ListLink(ConceptNode("A"), ConceptNode("B"))))


def get_variable(variable):
    return ConceptNode('Variable-' + variable.name)


print("variable: ", get_variable(ConceptNode("A")))


prob_key = PredicateNode("probability")

def move_value(key, atom_from, atom_to):
    value = atom_from.get_value(key)
    atom_to.set_value(key, value)
    return ConceptNode('Test')

prob_key = ConceptNode("probability")
c1 = ConceptNode("C1")
c1.set_value(prob_key, StringValue("123"))
c2 = ConceptNode("C2")

move_value(prob_key, c1, c2)

print("value: ", c2.get_value(prob_key))

except_factor = ConceptNode('F')

bind_link = BindLink(
    VariableNode('$F'),
    AndLink(
        EvaluationLink(
            PredicateNode('factor-node'),
            VariableNode('$F'))
    ),
    VariableNode('$F'))

values_link = bindlink(atomspace, bind_link)
