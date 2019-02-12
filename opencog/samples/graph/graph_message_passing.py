from opencog.bindlink import execute_atom, evaluate_atom
from opencog.type_constructors import *
from opencog.utilities import initialize_opencog

# AtomSpace Initialization
atomspace = AtomSpace()
initialize_opencog(atomspace)

TV_FALSE = TruthValue(0, 1)
TV_TRUE = TruthValue(1, 1)

NODE_KEY = PredicateNode('node')
EDGE_KEY = PredicateNode('edge')
DIRECTED_EDGE_KEY = PredicateNode('directed-edge')
MESSAGE_KEY = PredicateNode('message')
MESSAGE_PATH_KEY = PredicateNode('message-path-key')


def get_node(n):
    return EvaluationLink(NODE_KEY, n)


def get_edge(a, b):
    return EvaluationLink(EDGE_KEY, ListLink(a, b))


def get_directed_edge(a, b):
    return EvaluationLink(DIRECTED_EDGE_KEY, ListLink(a, b))


def get_message(a, b):
    return EvaluationLink(MESSAGE_KEY, ListLink(a, b))


def get_message_path(v, v1, v2):
    return EvaluationLink(MESSAGE_PATH_KEY, ListLink(v, v1, v2))


# Graph
# A --- B --- C

node_a = ConceptNode("A")
node_b = ConceptNode("B")
node_c = ConceptNode("C")

get_edge(node_a, node_b)
get_edge(node_b, node_c)

create_initial_messages_rule = BindLink(
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
        AbsentLink(
            get_edge(VariableNode('$V'), VariableNode('$V1'))
        ),
        get_edge(VariableNode('$V1'), VariableNode('$V2'))
    ),
    get_message(VariableNode('$V1'), VariableNode('$V2'))
)

res = execute_atom(atomspace, create_initial_messages_rule)
print(res)
