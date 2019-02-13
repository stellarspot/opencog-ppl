from opencog.bindlink import execute_atom
from opencog.type_constructors import *
from opencog.utilities import initialize_opencog

# AtomSpace Initialization
atomspace = AtomSpace()
initialize_opencog(atomspace)

NODE_KEY = PredicateNode('node')
EDGE_KEY = PredicateNode('edge')
DIRECTED_EDGE_KEY = PredicateNode('directed-edge')
MESSAGE_KEY = PredicateNode('message')


def get_node(n):
    return EvaluationLink(NODE_KEY, n)


def get_edge(a, b):
    return EvaluationLink(EDGE_KEY, ListLink(a, b))


def get_directed_edge(a, b):
    return EvaluationLink(DIRECTED_EDGE_KEY, ListLink(a, b))


def get_message(a, b):
    return EvaluationLink(MESSAGE_KEY, ListLink(a, b))


def calculate_message_value(messages):
    a = 0.8
    value = 1.0

    for message in messages.get_out():
        val = message.get_value(MESSAGE_KEY).to_list()[0]
        value += a * val

    return value


def set_message_value(m, value):
    m.set_value(MESSAGE_KEY, FloatValue(value))


def send_initial_message(m, v1, v2):
    print('send initial message:', v1.name, v2.name)
    set_message_value(m, calculate_message_value(SetLink()))
    return m


def send_message(msg, v1, v2, messages):
    print('send message:', v1.name, v2.name)
    set_message_value(msg, calculate_message_value(messages))
    return msg


def set_node_message(node, v1, messages):
    value = 1.0
    for message in messages.get_out():
        val = message.get_value(MESSAGE_KEY).to_list()[0]
        value *= val

    node.set_value(MESSAGE_KEY, FloatValue(value))
    return node


# Graph
# A --- B --- C

# node_a = ConceptNode("A")
# node_b = ConceptNode("B")
# node_c = ConceptNode("C")
#
# get_edge(node_a, node_b)
# get_edge(node_b, node_c)

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

# Get all incoming messages for the given vertex
DefineLink(
    DefinedSchemaNode("get_all_incoming_messages"),
    LambdaLink(
        TypedVariableLink(
            VariableNode('$V1'),
            TypeNode('ConceptNode')),
        BindLink(
            TypedVariableLink(
                VariableNode('$V'),
                TypeNode('ConceptNode')),
            get_message(VariableNode('$V'), VariableNode('$V1')),
            get_message(VariableNode('$V'), VariableNode('$V1')))
    ))

# Get all incoming messages except excluded for the given vertex
DefineLink(
    DefinedSchemaNode("get_incoming_messages"),
    LambdaLink(
        VariableList(
            TypedVariableLink(
                VariableNode('$V1'),
                TypeNode('ConceptNode')),
            TypedVariableLink(
                VariableNode('$V2'),
                TypeNode('ConceptNode'))),
        BindLink(
            TypedVariableLink(
                VariableNode('$V'),
                TypeNode('ConceptNode')),
            AndLink(
                get_message(VariableNode('$V'), VariableNode('$V1')),
                NotLink(
                    EqualLink(
                        VariableNode('$V'),
                        VariableNode('$V2')))),
            get_message(VariableNode('$V'), VariableNode('$V1')))))

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
                            VariableNode('$V2')))),
                VariableNode('$V')),
            SetLink()),
        get_directed_edge(VariableNode('$V1'), VariableNode('$V2'))),
    ExecutionOutputLink(
        GroundedSchemaNode('py: send_initial_message'),
        ListLink(
            get_message(VariableNode('$V1'), VariableNode('$V2')),
            VariableNode('$V1'),
            VariableNode('$V2')))
)

create_messages_rule = BindLink(
    VariableList(
        TypedVariableLink(
            VariableNode('$V1'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$V2'),
            TypeNode('ConceptNode'))),
    AndLink(
        get_directed_edge(VariableNode('$V1'), VariableNode('$V2')),
        AbsentLink(
            get_message(VariableNode('$V1'), VariableNode('$V2'))),
        EqualLink(
            BindLink(
                TypedVariableLink(
                    VariableNode('$V'),
                    TypeNode('ConceptNode')),
                AndLink(
                    get_directed_edge(VariableNode('$V'), VariableNode('$V1')),
                    NotLink(
                        EqualLink(
                            VariableNode('$V'),
                            VariableNode('$V2')))),
                VariableNode('$V')),
            BindLink(
                TypedVariableLink(
                    VariableNode('$V'),
                    TypeNode('ConceptNode')),
                AndLink(
                    get_message(VariableNode('$V'), VariableNode('$V1')),
                    NotLink(
                        EqualLink(
                            VariableNode('$V'),
                            VariableNode('$V2')))),
                VariableNode('$V'))
        )),
    ExecutionOutputLink(
        GroundedSchemaNode('py: send_message'),
        ListLink(
            get_message(VariableNode('$V1'), VariableNode('$V2')),
            VariableNode('$V1'),
            VariableNode('$V2'),
            PutLink(
                DefinedSchemaNode("get_incoming_messages"),
                ListLink(
                    VariableNode('$V1'),
                    VariableNode('$V2'))))))

create_node_value_rule = BindLink(
    TypedVariableLink(
        VariableNode('$V1'),
        TypeNode('ConceptNode')),
    get_node(VariableNode("$V1")),
    ExecutionOutputLink(
        GroundedSchemaNode('py: set_node_message'),
        ListLink(
            get_node(VariableNode("$V1")),
            VariableNode('$V1'),
            PutLink(
                DefinedSchemaNode("get_all_incoming_messages"),
                VariableNode('$V1')))))


def run_message_passing():
    res = execute_atom(atomspace, directed_message_edge_creation_rule)
    # print("create directed graph")
    # print(res)

    res = execute_atom(atomspace, create_initial_messages_rule)
    # print('send initial messages')
    # print(res)
    res = execute_atom(atomspace, create_messages_rule)
    res = execute_atom(atomspace, create_messages_rule)
    # print('send messages')
    # print(res)
    res = execute_atom(atomspace, create_node_value_rule)
    # print(res)
    pass


def show_results():
    # Print result
    # Show all messages
    all_messages_rule = GetLink(
        VariableList(
            TypedVariableLink(
                VariableNode('$V1'),
                TypeNode('ConceptNode')),
            TypedVariableLink(
                VariableNode('$V2'),
                TypeNode('ConceptNode'))),
        get_message(VariableNode('$V1'), VariableNode('$V2')))

    all_messages = execute_atom(atomspace, all_messages_rule)

    for listLink in all_messages.get_out():
        v1 = listLink.get_out()[0]
        v2 = listLink.get_out()[1]
        value = get_message(v1, v2).get_value(MESSAGE_KEY)
        print('message:', v1.name, v2.name, value.to_list())

    all_nodes_rule = GetLink(
        TypedVariableLink(
            VariableNode('$V1'),
            TypeNode('ConceptNode')),
        get_node(VariableNode('$V1')))

    all_nodes = execute_atom(atomspace, all_nodes_rule)

    for vertex in all_nodes.get_out():
        value = get_node(vertex).get_value(MESSAGE_KEY)
        print('node:', vertex.name, value.to_list())


run_message_passing()
show_results()
