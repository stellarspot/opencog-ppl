from opencog.bindlink import execute_atom, evaluate_atom
from opencog.type_constructors import *
from opencog.utilities import initialize_opencog

# AtomSpace Initialization
atomspace = AtomSpace()
initialize_opencog(atomspace)

TV_FALSE = TruthValue(0, 1)
TV_TRUE = TruthValue(1, 1)

NODE_KEY = PredicateNode('edge')
EDGE_KEY = PredicateNode('edge')
DIRECTED_EDGE_KEY = PredicateNode('directed-edge')
MESSAGE_KEY = PredicateNode('message')
MESSAGE_PATH_KEY = PredicateNode('message-path-key')


def get_node(n):
    return EvaluationLink(NODE_KEY, n)


def get_edge(a, b):
    return EvaluationLink(EDGE_KEY, ListLink(a, b))


def get_message(a, b):
    return EvaluationLink(MESSAGE_KEY, ListLink(a, b))


def get_message_path(v, v1, v2):
    return EvaluationLink(MESSAGE_PATH_KEY, ListLink(v, v1, v2))


def get_directed_edge(a, b):
    return EvaluationLink(DIRECTED_EDGE_KEY, ListLink(a, b))


# Graph
# A - +
#     C --- D --- E
# B - +

node_a = ConceptNode("A")
node_b = ConceptNode("B")
node_c = ConceptNode("C")
node_d = ConceptNode("D")
node_e = ConceptNode("E")

get_edge(node_a, node_c)
get_edge(node_b, node_c)
get_edge(node_c, node_d)
get_edge(node_d, node_e)

directed_message_edge_creation_rule = BindLink(
    VariableList(
        TypedVariableLink(
            VariableNode('$V1'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$V2'),
            TypeNode('ConceptNode'))),
    get_edge(
        VariableNode('$V1'),
        VariableNode('$V2')),
    ListLink(
        get_node(VariableNode('$V1')),
        get_node(VariableNode('$V2')),
        get_directed_edge(
            VariableNode('$V1'),
            VariableNode('$V2')),
        get_directed_edge(
            VariableNode('$V2'),
            VariableNode('$V1'))))

create_message_path_rule = BindLink(
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
        NotLink(
            EqualLink(
                VariableNode('$V'),
                VariableNode('$V2'))),
        AbsentLink(
            EvaluationLink(
                MESSAGE_KEY,
                ListLink(
                    VariableNode("$V1"),
                    VariableNode("$V2")))),
        # Pattern clauses
        get_directed_edge(
            VariableNode('$V'),
            VariableNode('$V1')),
        get_directed_edge(
            VariableNode('$V1'),
            VariableNode('$V2'))
    ),
    get_message_path(
        VariableNode('$V'),
        VariableNode('$V1'),
        VariableNode('$V2')))

res = execute_atom(atomspace, directed_message_edge_creation_rule)
# print(res)

# get_message(node_a, node_c)
# get_message(node_b, node_c)
# get_message(node_c, node_d)
#
# get_message(node_c, node_a)
# get_message(node_c, node_b)
# get_message(node_d, node_c)

res = execute_atom(atomspace, create_message_path_rule)
print(res)
