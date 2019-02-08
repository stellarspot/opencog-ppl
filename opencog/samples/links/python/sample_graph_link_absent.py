from opencog.bindlink import execute_atom, evaluate_atom
from opencog.type_constructors import *
from opencog.utilities import initialize_opencog

# AtomSpace Initialization
atomspace = AtomSpace()
initialize_opencog(atomspace)

EDGE_KEY = PredicateNode('edge')
MESSAGE_KEY = PredicateNode('message')


def get_edge(a, b):
    return EvaluationLink(EDGE_KEY, ListLink(a, b))


def get_message(a, b):
    return EvaluationLink(MESSAGE_KEY, ListLink(a, b))


# Graph
# A --- B --- C

node_a = ConceptNode("A")
node_b = ConceptNode("B")
node_c = ConceptNode("C")

get_edge(node_a, node_b)
get_edge(node_b, node_c)

create_initial_message_rule = BindLink(
    VariableList(
        TypedVariableLink(
            VariableNode('$V'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$V1'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$V2'),
            TypeNode('ConceptNode'))),

    AndLink(
        # Preconditions
        AbsentLink(
            get_message(
                VariableNode("$V1"),
                VariableNode("$V2"))),
        AbsentLink(
            get_edge(
                VariableNode('$V'),
                VariableNode('$V1'))),
        PresentLink(
            VariableNode("$V")),
        # Pattern clauses
        get_edge(
            VariableNode('$V1'),
            VariableNode('$V2'))
    ),
    get_message(
        VariableNode('$V1'),
        VariableNode('$V2')))

res = execute_atom(atomspace, create_initial_message_rule)
print(res)
