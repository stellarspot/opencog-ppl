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


# MESSAGE_PATH_KEY = PredicateNode('message-path-key')


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


def set_message_value(m, value):
    m.set_value(MESSAGE_KEY, FloatValue(value))


def send_initial_message(m, v1, v2):
    set_message_value(m, 1.0)
    return m


# Graph
# A --- B --- C

node_a = ConceptNode("A")
node_b = ConceptNode("B")
node_c = ConceptNode("C")

get_edge(node_a, node_b)
get_edge(node_b, node_c)

# get_edge(node_a, node_b)
# get_edge(node_a, node_c)


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
        get_directed_edge(
            VariableNode('$V1'),
            VariableNode('$V2')),
        get_directed_edge(
            VariableNode('$V2'),
            VariableNode('$V1'))))

res = execute_atom(atomspace, directed_message_edge_creation_rule)
# print("create directed graph")
# print(res)


create_initial_messages_rule = BindLink(
    VariableList(
        TypedVariableLink(
            VariableNode('$V1'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$V2'),
            TypeNode('ConceptNode'))),
    AndLink(
        EqualLink(
            BindLink(
                TypedVariableLink(
                    VariableNode('$V'),
                    TypeNode('ConceptNode')),
                AndLink(
                    get_directed_edge(VariableNode('$V1'), VariableNode('$V')),
                    NotLink(
                        EqualLink(
                            VariableNode('$V'),
                            VariableNode('$V2')
                        )
                    )
                ),
                VariableNode('$V')
            ),
            SetLink()
        ),
        get_directed_edge(VariableNode('$V1'), VariableNode('$V2'))
    ),
    ExecutionOutputLink(
        GroundedSchemaNode('py: send_initial_message'),
        ListLink(
            get_message(VariableNode('$V1'), VariableNode('$V2')),
            VariableNode('$V1'),
            VariableNode('$V2')))
)

res = execute_atom(atomspace, create_initial_messages_rule)
print('send initial messages')
print(res)
