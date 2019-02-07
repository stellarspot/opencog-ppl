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


def get_directed_message_edge(a, b):
    return EvaluationLink(DIRECTED_MESSAGE_EDGE_KEY, ListLink(a, b))


def has_message(edge):
    return TV_TRUE if edge.get_value(MESSAGE_KEY) else TV_FALSE


def set_message_value(v1, v2, message):
    get_directed_message_edge(v1, v2).set_value(MESSAGE_KEY, FloatValue(message))


def get_message_value(v1, v2):
    value = get_directed_message_edge(v1, v2).get_value(MESSAGE_KEY)
    # Workaround
    value = FloatValue(0, value=value)
    return int(value.to_list()[0])


def get_neigbours(v):
    neighbour_nodes_rule = BindLink(
        TypedVariableLink(
            VariableNode('$V'),
            TypeNode('ConceptNode')),
        AndLink(
            # Pattern clauses
            get_directed_message_edge(
                VariableNode('$V'),
                v)),
        VariableNode('$V'))

    return execute_atom(atomspace, neighbour_nodes_rule)


def get_neigbours_except(v1, v2):
    neighbour_nodes_rule = BindLink(
        TypedVariableLink(
            VariableNode('$V'),
            TypeNode('ConceptNode')),
        AndLink(
            # Preconditions
            NotLink(
                EqualLink(
                    VariableNode('$V'),
                    v2)),
            # Pattern clauses
            get_directed_message_edge(
                VariableNode('$V'),
                v1)),
        VariableNode('$V'))

    return execute_atom(atomspace, neighbour_nodes_rule)


def can_send_message(v1, v2):
    neigbor_nodes = get_neigbours_except(v1, v2)

    for v in neigbor_nodes.out:
        if has_message(get_directed_message_edge(v, v1)) == TV_FALSE:
            return TV_FALSE

    return TV_TRUE


def send_message(v1, v2):
    neigbor_nodes = get_neigbours_except(v1, v2)

    message = 1

    for v in neigbor_nodes.out:
        msg = get_message_value(v, v1)
        message += msg

    print('   send message:', v1.name, "->", v2.name, message)

    set_message_value(v1, v2, message)
    return get_directed_message_edge(v1, v2)


def get_node_value(n):
    neigbours = get_neigbours(n)
    message = 0
    for v in neigbours.out:
        msg = get_message_value(v, n)
        message += msg

    return message


# Graph
# A - +     + - D
#     C --- F
# B - +     + - E
get_edge(get_node("A"), get_node("C"))
get_edge(get_node("B"), get_node("C"))
get_edge(get_node("D"), get_node("F"))
get_edge(get_node("E"), get_node("F"))
get_edge(get_node("C"), get_node("F"))

nodes = [get_node("A"),
         get_node("B"),
         get_node("C"),
         get_node("D"),
         get_node("E"),
         get_node("F")]

# Graph
# A - +
#     C --- E --- D --- F
# B - +

# get_edge(get_node("A"), get_node("C"))
# get_edge(get_node("B"), get_node("C"))
# get_edge(get_node("D"), get_node("E"))
# get_edge(get_node("C"), get_node("E"))
# get_edge(get_node("F"), get_node("D"))
#
# nodes = [get_node("A"),
#          get_node("B"),
#          get_node("C"),
#          get_node("D"),
#          get_node("E"),
#          get_node("F")]

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
        get_directed_message_edge(
            VariableNode('$V1'),
            VariableNode('$V2')),
        get_directed_message_edge(
            VariableNode('$V2'),
            VariableNode('$V1'))))

message_sending_rule = BindLink(
    VariableList(
        TypedVariableLink(
            VariableNode('$V1'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$V2'),
            TypeNode('ConceptNode'))),

    AndLink(
        # Preconditions
        NotLink(
            EvaluationLink(
                GroundedPredicateNode('py: has_message'),
                ListLink(
                    get_directed_message_edge(
                        VariableNode('$V1'),
                        VariableNode('$V2'))))),
        EvaluationLink(
            GroundedPredicateNode('py: can_send_message'),
            ListLink(
                VariableNode('$V1'),
                VariableNode('$V2')
            )),
        # Pattern clauses
        get_directed_message_edge(
            VariableNode('$V1'),
            VariableNode('$V2'))
    ),
    ExecutionOutputLink(
        GroundedSchemaNode('py: send_message'),
        ListLink(
            VariableNode('$V1'),
            VariableNode('$V2'))))

res = execute_atom(atomspace, directed_message_edge_creation_rule)
# print(res)

print("=== iter 1 ===")
res = execute_atom(atomspace, message_sending_rule)
print("=== iter 2 ===")
res = execute_atom(atomspace, message_sending_rule)
print("=== iter 3 ===")
res = execute_atom(atomspace, message_sending_rule)

# set_message(get_node("A"), get_node("C"), 1)
# set_message(get_node("B"), get_node("C"), 1)
#
# send_message(get_node("C"), get_node("D"))

for node in nodes:
    msg = get_node_value(node)
    print('node:', node.name, "value:", msg)
