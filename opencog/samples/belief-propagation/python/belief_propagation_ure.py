from opencog.utilities import initialize_opencog
from opencog.type_constructors import *
from opencog.bindlink import bindlink
from opencog.bindlink import execute_atom

# AtomSpace Initialization
atomspace = AtomSpace()
initialize_opencog(atomspace)

CDV_KEY = PredicateNode('CDV')
SHAPE_KEY = PredicateNode('shape')

FACTOR_KEY = PredicateNode('factor')
VARIABLE_KEY = PredicateNode('variable')
EDGE_KEY = PredicateNode('edge')
TENSOR_KEY = PredicateNode('tensor')

MESSAGE_VARIABLE_FACTOR_KEY = PredicateNode('message-variable-factor')
MESSAGE_FACTOR_VARIABLE_KEY = PredicateNode('message-factor-variable')

TRUTH_VALUE_FALSE = TruthValue(0, 1)
TRUTH_VALUE_TRUE = TruthValue(1, 1)


# Utility methods

def show_atomspace():
    print('--- AtomSpace Dump---')
    for atom in atomspace:
        print(atom)
    print('---------------------')


# Belief Propagation Utility methods

def bool_to_tv(b):
    if not b:
        return TRUTH_VALUE_FALSE
    return TRUTH_VALUE_TRUE


def float_value_to_list(value):
    list = None
    if value:
        list = value.to_list()
    return list


def has_value(atom, key):
    """
    :param atom: the given atom
    :param key: the given key
    :return: True if the atom contains a value for the given key
    """
    value = atom.get_value(key)
    if value:
        return True
    return False


def eval_has_value(atom, key):
    value = atom.get_value(key)
    if value:
        return TRUTH_VALUE_TRUE
    return TRUTH_VALUE_FALSE


def eval_has_dv(atom):
    return eval_has_value(atom, CDV_KEY)


def show_value(msg, atom, key):
    value = atom.get_value(key)
    if value:
        print(msg + ':', float_value_to_list(value))


def show_values(atom, msg=''):
    if msg:
        print(msg)

    show_value('cdv', atom, CDV_KEY)
    show_value('shape', atom, SHAPE_KEY)
    show_value('tensor', atom, TENSOR_KEY)
    print()


# Factor Graph methods

def get_variable_node(v):
    name = 'Variable-' + v.name
    return ConceptNode(name)


def get_factor_node(variables):
    names = list(map(lambda v: v.name, variables))
    names.sort()
    name = 'Factor-' + '-'.join(names)
    return ConceptNode(name)


def get_variable_predicate(variable):
    return EvaluationLink(
        VARIABLE_KEY,
        variable
    )


def get_factor_predicate(factor):
    return EvaluationLink(
        FACTOR_KEY,
        factor
    )


def get_edge_predicate(factor, var):
    return EvaluationLink(
        EDGE_KEY,
        ListLink(
            factor,
            var
        )
    )


def set_variable_shape(v, variable):
    shape = v.get_value(SHAPE_KEY)
    if shape:
        variable.set_value(SHAPE_KEY, shape)


def set_factor_tensor(atom, factor):
    shape = atom.get_value(SHAPE_KEY)
    factor.set_value(SHAPE_KEY, shape)
    tensor = atom.get_value(CDV_KEY)
    factor.set_value(TENSOR_KEY, tensor)


def get_neighbors_factors(variable, exclude_factor):
    bind_link = BindLink(
        VariableNode('$F'),
        AndLink(
            get_factor_predicate(
                VariableNode('$F')),
            get_edge_predicate(
                VariableNode('$F'),
                variable),
            NotLink(
                EqualLink(
                    exclude_factor,
                    VariableNode('$F')))),
        VariableNode('$F'))

    factors_link = bindlink(atomspace, bind_link)
    return factors_link


def can_send_message_variable_factor(variable, factor):
    """
    Check that message can be send from variable to factor:
    - there is no a message from the variable to factor
    - all edges from factors to the variable except the
      the given factor have messages

    :param variable: variable in factor factor graph
    :param factor: factor in factor factor graph
    :return: TruthValue indicates that message can be send
    """

    # print('can_send_message_variable_factor', variable.name, factor.name)

    edge = get_edge_predicate(variable, factor)

    if has_value(edge, MESSAGE_VARIABLE_FACTOR_KEY):
        return TRUTH_VALUE_FALSE

    factors = get_neighbors_factors(variable, factor).out

    if not factors:
        return TRUTH_VALUE_TRUE

    return TRUTH_VALUE_FALSE

def can_send_message_factor_variable(factor, variable):
    """
    Check that message can be send from factor to variable :
    - there is no a message from the factor to variable
    - all edges from variables to the factor except the
      the given variable have messages

    :param factor: factor in factor factor graph
    :param variable: variable in factor factor graph
    :return: TruthValue indicates that message can be send
    """

    # print('can_send_message_variable_factor', variable.name, factor.name)

    # edge = get_edge_predicate(variable, factor)
    #
    # if has_value(edge, MESSAGE_VARIABLE_FACTOR_KEY):
    #     return TRUTH_VALUE_FALSE
    #
    # factors = get_neighbors_factors(variable, factor).out
    #
    # if not factors:
    #     return TRUTH_VALUE_TRUE

    return TRUTH_VALUE_FALSE


def get_initial_message_variable(variable):
    """
    :param variable: variable in factor factor graph
    :return: [1.0] * variable shape
    """
    shape = variable.get_value(SHAPE_KEY)
    assert shape, 'Variable shape must be set: ' + variable.name
    return [1.0] * int(shape.to_list()[0])


def set_message_edge(edge, message):
    """
    Sets the message to graph edge.

    :param edge: edge in factor graph
    :param message: python list of float values
    """

    value = FloatValue(message)
    edge.set_value(MESSAGE_VARIABLE_FACTOR_KEY, value)


def create_message_variable_factor(variable, factor):
    print('create_message_variable_factor', variable.name, factor.name)
    factors = get_neighbors_factors(variable, factor).out
    # print('factors:', factors)

    if not factors:
        edge = get_edge_predicate(variable, factor)
        msg = get_initial_message_variable(variable)
        set_message_edge(edge, msg)


def init_factor_graph():
    init_factor_graph_concept_node()
    init_factor_graph_implication_link()


def send_messages():
    send_message_variable_factor()


# ; =====================================================================
# ; ConceptNode to Variable rule
# ;
# ; A
# ; |-
# ; Evaluation
# ;    Predicate "factor"
# ;    Concept "Factor-A"
# ;
# ; Evaluation
# ;    Predicate "variable"
# ;    Concept "Variable-A"
# ;
# ; Evaluation
# ;    Predicate "edge"
# ;    List
# ;        Concept "Factor-A"
# ;        Concept "Variable-A"
# ;----------------------------------------------------------------------

def init_factor_graph_concept_node():
    bind_link = BindLink(
        TypedVariableLink(
            VariableNode('$V'),
            TypeNode('ConceptNode')),
        EvaluationLink(
            GroundedPredicateNode('py: eval_has_dv'),
            ListLink(
                VariableNode('$V'))),
        ExecutionOutputLink(
            GroundedSchemaNode('py: init_factor_graph_concept_node_formula'),
            ListLink(
                VariableNode('$V'))))
    bindlink(atomspace, bind_link)
    # print(bindlink(atomspace, bind_link))


def init_factor_graph_concept_node_formula(v):
    print('init_factor_graph_concept_node_formula', v)

    variable = get_variable_node(v)
    factor = get_factor_node([v])

    # generate factor graph predicates
    variable_predicate = get_variable_predicate(variable)
    factor_predicate = get_factor_predicate(factor)
    edge = get_edge_predicate(factor, variable)

    # set variable shape
    set_variable_shape(v, variable)

    # set factor tensor
    set_factor_tensor(v, factor)

    return ListLink(
        variable_predicate,
        factor_predicate,
        edge
    )


# ; =====================================================================
# ; Implication to Variable rule
# ;
# ; Implication
# ;   A
# ;   B
# ; |-
# ; Evaluation
# ;    Predicate "factor"
# ;    Concept "Factor-A-B"
# ;
# ; Evaluation
# ;    Predicate "variable"
# ;    Concept "Variable-A"
# ;
# ; Evaluation
# ;    Predicate "variable"
# ;    Concept "Variable-B"
# ;
# ; Evaluation
# ;    Predicate "edge"
# ;    List
# ;        Concept "Factor-A-B"
# ;        Concept "Variable-A"
# ;
# ; Evaluation
# ;    Predicate "edge"
# ;    List
# ;        Concept "Factor-A-B"
# ;        Concept "Variable-B"
# ;----------------------------------------------------------------------

def init_factor_graph_implication_link():
    bind_link = BindLink(
        VariableList(
            TypedVariableLink(
                VariableNode('$V1'),
                TypeNode('ConceptNode')),
            TypedVariableLink(
                VariableNode('$V2'),
                TypeNode('ConceptNode'))),

        AndLink(
            # Preconditions
            EvaluationLink(
                GroundedPredicateNode('py: eval_has_dv'),
                ListLink(
                    ImplicationLink(
                        VariableNode('$V1'),
                        VariableNode('$V2')))),
            # Pattern clauses
            ImplicationLink(
                VariableNode('$V1'),
                VariableNode('$V2'))),
        ExecutionOutputLink(
            GroundedSchemaNode('py: init_factor_graph_implication_link_formula'),
            ListLink(
                VariableNode('$V1'),
                VariableNode('$V2'))))
    bindlink(atomspace, bind_link)
    # print(bindlink(atomspace, bind_link))


def init_factor_graph_implication_link_formula(v1, v2):
    print('init_factor_graph_implication_link_formula', v1.name, v2.name)

    variable1 = get_variable_node(v1)
    variable2 = get_variable_node(v2)
    factor = get_factor_node([v1, v2])

    # generate factor graph predicates
    variable_predicate_1 = get_variable_predicate(variable1)
    variable_predicate_2 = get_variable_predicate(variable2)
    factor_predicate = get_factor_predicate(factor)
    edge1 = get_edge_predicate(factor, variable1)
    edge2 = get_edge_predicate(factor, variable2)

    # set variable shape
    set_variable_shape(v1, variable1)
    set_variable_shape(v2, variable2)

    # # set factor tensor
    # set_factor_tensor(v, factor)

    return ListLink(
        variable_predicate_1,
        variable_predicate_2,
        factor_predicate,
        edge1,
        edge2
    )


# ; =====================================================================
# ; Variable to Factor Message rule
# ;
# ; Evaluation
# ;    Predicate "variable-node"
# ;    A
# ; Evaluation
# ;    Predicate "factor-node"
# ;    F
# ; Evaluation
# ;    Predicate "graph-edge"
# ;    List
# ;        Concept F
# ;        Concept A
# ; |-
# ;
# ; Evaluation
# ;    Predicate "graph-message"
# ;    List
# ;        Concept A
# ;        Concept F
# ;----------------------------------------------------------------------


def send_message_variable_factor():
    bind_link = BindLink(
        VariableList(
            TypedVariableLink(
                VariableNode('$V'),
                TypeNode('ConceptNode')),
            TypedVariableLink(
                VariableNode('$F'),
                TypeNode('ConceptNode'))),

        AndLink(
            NotLink(
                EvaluationLink(
                    GroundedPredicateNode('py: eval_has_value'),
                    ListLink(
                        get_edge_predicate(
                            VariableNode('$V'),
                            VariableNode('$F')),
                        MESSAGE_VARIABLE_FACTOR_KEY))),
            EvaluationLink(
                GroundedPredicateNode('py: can_send_message_variable_factor'),
                ListLink(
                    VariableNode('$V'),
                    VariableNode('$F')
                )),
            # Pattern clauses
            EvaluationLink(
                VARIABLE_KEY,
                VariableNode('$V')
            ),
            EvaluationLink(
                FACTOR_KEY,
                VariableNode('$F')
            ),
        ),
        ExecutionOutputLink(
            GroundedSchemaNode('py: send_message_variable_factor_formula'),
            ListLink(
                VariableNode('$V'),
                VariableNode('$F'))))
    bindlink(atomspace, bind_link)
    # print(bindlink(atomspace, bind_link))


def send_message_variable_factor_formula(variable, formula):
    # print('send_message_variable_factor_formula', variable.name, formula.name)
    create_message_variable_factor(variable, formula)
    return ListLink()


# ; =====================================================================
# ; Factor to Variable Message rule
# ;
# ; Evaluation
# ;    Predicate "factor-node"
# ;    F
# ; Evaluation
# ;    Predicate "variable-node"
# ;    A
# ; Evaluation
# ;    Predicate "graph-edge"
# ;    List
# ;        Concept F
# ;        Concept A
# ; |-
# ;
# ; Evaluation
# ;    Predicate "graph-message"
# ;    List
# ;        Concept F
# ;        Concept A
# ;----------------------------------------------------------------------

def send_message_factor_variable():
    bind_link = BindLink(
        VariableList(
            TypedVariableLink(
                VariableNode('$F'),
                TypeNode('ConceptNode')),
            TypedVariableLink(
                VariableNode('$V'),
                TypeNode('ConceptNode'))),

        AndLink(
            NotLink(
                EvaluationLink(
                    GroundedPredicateNode('py: eval_has_value'),
                    ListLink(
                        get_edge_predicate(
                            VariableNode('$F'),
                            VariableNode('$V')),
                        MESSAGE_FACTOR_VARIABLE_KEY))),
            EvaluationLink(
                GroundedPredicateNode('py: can_send_message_factor_variable'),
                ListLink(
                    VariableNode('$F'),
                    VariableNode('$V')
                )),
            # Pattern clauses
            EvaluationLink(
                FACTOR_KEY,
                VariableNode('$F')
            ),
            EvaluationLink(
                VARIABLE_KEY,
                VariableNode('$V')
            ),
        ),
        ExecutionOutputLink(
            GroundedSchemaNode('py: send_message_factor_variable_formula'),
            ListLink(
                VariableNode('$F'),
                VariableNode('$V'))))
    bindlink(atomspace, bind_link)
    # print(bindlink(atomspace, bind_link))


def send_message_factor_variable_formula(factor, variable):
    print('send_message_factor_variable_formula', factor.name, variable.name)
    # create_message_factor_variable(variable, formula)
    return ListLink()
