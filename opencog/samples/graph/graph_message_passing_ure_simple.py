from opencog.ure import BackwardChainer
from opencog.bindlink import execute_atom
from opencog.type_constructors import *
from opencog.utilities import initialize_opencog

atomspace = AtomSpace()
initialize_opencog(atomspace)

TV_TRUE = TruthValue(1.0, 1.0)

EDGE_KEY = PredicateNode('edge')
DIRECTED_EDGE_KEY = PredicateNode('directed-edge')
MESSAGE_KEY = PredicateNode('message')


def get_directed_edge(a, b):
    directed_edge = EvaluationLink(DIRECTED_EDGE_KEY, ListLink(a, b))
    directed_edge.tv = TV_TRUE
    return directed_edge


def get_message(a, b):
    return EvaluationLink(MESSAGE_KEY, ListLink(a, b))


def send_initial_message(m, v1, v2):
    print('send initial message:', v1.name, v2.name)
    m.tv = TV_TRUE
    return m


def send_message(msg, v1, v2, messages):
    print('send message:', v1.name, v2.name)
    msg.tv = TV_TRUE
    return msg


# Graph
# A --- B --- C --- D

node_a = ConceptNode("A")
node_b = ConceptNode("B")
node_c = ConceptNode("C")
node_d = ConceptNode("D")

get_directed_edge(node_a, node_b)
get_directed_edge(node_b, node_a)

get_directed_edge(node_b, node_c)
get_directed_edge(node_c, node_b)

get_directed_edge(node_c, node_d)
get_directed_edge(node_d, node_c)

# Send initial messages

send_initial_message(get_message(node_a, node_b), node_a, node_b)
send_initial_message(get_message(node_d, node_c), node_d, node_c)

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

# Create message rule

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


def run_message_passing():
    res = execute_atom(atomspace, create_messages_rule)
    res = execute_atom(atomspace, create_messages_rule)


def run_message_passing_ure():
    fc_message_sending_rule_name = DefinedSchemaNode("fc-message-sending-rule")

    DefineLink(
        fc_message_sending_rule_name,
        create_messages_rule)

    fc_message_sending_rbs = ConceptNode("fc-message-sending-rule")

    InheritanceLink(
        fc_message_sending_rbs,
        ConceptNode("URE")
    )

    MemberLink(
        fc_message_sending_rule_name,
        fc_message_sending_rbs
    )

    # Set URE maximum-iterations
    from opencog.scheme_wrapper import scheme_eval

    execute_code = \
        '''
        (use-modules (opencog rule-engine))
        (ure-set-num-parameter (ConceptNode "fc-message-sending-rbs") "URE:maximum-iterations" 30)
        '''

    scheme_eval(atomspace, execute_code)

    chainer = BackwardChainer(atomspace,
                              ConceptNode("fc-message-sending-rule"),
                              get_message(VariableNode("$V1"), VariableNode("$V2")),
                              VariableList(
                                  TypedVariableLink(VariableNode("$V1"), TypeNode("ConceptNode")),
                                  TypedVariableLink(VariableNode("$V2"), TypeNode("ConceptNode"))))

    chainer.do_chain()
    results = chainer.get_results()


# run_message_passing()
run_message_passing_ure()
