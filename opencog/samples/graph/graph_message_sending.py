from opencog.utilities import initialize_opencog
from opencog.type_constructors import *
from opencog.bindlink import execute_atom

# AtomSpace Initialization
atomspace = AtomSpace()
initialize_opencog(atomspace)

TV_FALSE = TruthValue(0, 1)
TV_TRUE = TruthValue(1, 1)

EDGE_KEY = PredicateNode('edge')
MESSAGE_KEY = PredicateNode('message')
DIRECTED_MESSAGE_EDGE_KEY = PredicateNode('directed-message-edge')


def get_node(n):
    return ConceptNode(n)


def get_edge(a, b):
    return EvaluationLink(EDGE_KEY, ListLink(a, b))


def get_message(a, b):
    return EvaluationLink(MESSAGE_KEY, ListLink(a, b))


def get_directed_message_edge(a, b):
    return EvaluationLink(DIRECTED_MESSAGE_EDGE_KEY, ListLink(a, b))


def has_message(edge):
    return TV_TRUE if edge.get_value(MESSAGE_KEY) else TV_FALSE


# Graph
# A - +     + - D
#     C --- F
# E - +     + - E

get_edge(get_node("A"), get_node("C"))
get_edge(get_node("E"), get_node("C"))
get_edge(get_node("D"), get_node("F"))
get_edge(get_node("E"), get_node("F"))
get_edge(get_node("C"), get_node("F"))

directed_message_edge_creation_rule = BindLink(
    VariableList(
        TypedVariableLink(
            VariableNode('$X'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$Y'),
            TypeNode('ConceptNode'))),
    get_edge(
        VariableNode('$X'),
        VariableNode('$Y')),
    ListLink(
        get_directed_message_edge(
            VariableNode('$X'),
            VariableNode('$Y')),
        get_directed_message_edge(
            VariableNode('$Y'),
            VariableNode('$X'))))

message_sending_rule = BindLink(
    VariableList(
        TypedVariableLink(
            VariableNode('$X'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$Y'),
            TypeNode('ConceptNode'))),

    AndLink(
        # Preconditions
        NotLink(
            EvaluationLink(
                GroundedPredicateNode('py: has_message'),
                ListLink(
                    get_directed_message_edge(
                        VariableNode('$X'),
                        VariableNode('$Y'))))),
        # Pattern clauses
        get_directed_message_edge(
            VariableNode('$X'),
            VariableNode('$Y'))
    ),
    get_message(
        VariableNode('$X'),
        VariableNode('$Y')))

res = execute_atom(atomspace, directed_message_edge_creation_rule)
res = execute_atom(atomspace, message_sending_rule)

print(res)
