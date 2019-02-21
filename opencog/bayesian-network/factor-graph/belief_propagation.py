from opencog.type_constructors import *
from opencog.atomspace import PtrValue
from opencog.bindlink import execute_atom

import numpy as np

TV_TRUE = TruthValue(1.0, 1.0)
TV_FALSE = TruthValue(0.0, 0.0)


# Keys

def key_factor():
    return PredicateNode("factor")


def key_variable():
    return PredicateNode("variable")


def key_edge():
    return PredicateNode("edge")


def key_message():
    return PredicateNode("message")


def key_probability():
    return PredicateNode("probability")


def key_domain():
    return PredicateNode("domain")


def key_arguments():
    return PredicateNode("arguments")


def key_tensor():
    return PredicateNode("tensor")


# Factor Graph

def get_variable_node_name(v):
    """
    Adds 'Variable-' prefix + to the variable
    :param v: variable node
    :return: variable name with 'Variable-' prefix
    """
    return 'Variable-' + v.name


def get_variable_node(v):
    """
    Returns Variable node in factor graph
    The name of the variable node consists of 'Variable-' prefix and name of the original variable.

    :param v: original variable defined in Bayesian network
    :return: variable node in factor graph
    """
    return ConceptNode(get_variable_node_name(v))


def get_factor_node(variables):
    """
    Returns Factor node in factor graph.
    The name of the factor node consists of the 'Factor-' prefix and sorted list of the given variable names.

    :param variables: list of arguments the factor depends on
    :return: factor node in factor graph
    """
    names = [v.name for v in variables]
    names.sort()
    name = 'Factor-' + '-'.join(names)
    return ConceptNode(name)


def get_variable_predicate(variable):
    """
    Creates Variable predicate that allows to find variables in the factor graph
    :param variable: variable in factor graph
    :return: node which represents variable in the factor graph
    """
    return EvaluationLink(key_variable(), variable)


def get_factor_predicate(factor):
    """
    Creates Factor predicate predicate that allows to find factors in the factor graph
    :param factor: variable in factor graph
    :return: node which represents variable in the factor graph
    """
    return EvaluationLink(key_factor(), factor)


def get_edge_predicate(factor, variable):
    """
    Create an edge for the given factor and variable in the factor graph.
    Note, that the factor must always be the first argument and the variable the second.
    There are no edges from variables to factors.

    :param factor: factor in factor factor graph
    :param variable: variable in factor  graph
    :return: edge predicate for the given factor and variable
    """
    return EvaluationLink(
        key_edge(),
        ListLink(
            factor,
            variable))


def get_message_predicate(a, b):
    """
    Creates a message between nodes a and b
    :param a: node in the factor graph
    :param b: node in the factor graph
    :return: message predicate between nodes a and b
    """
    return EvaluationLink(
        key_message(),
        ListLink(
            a,
            b))


def get_messages_sources(node):
    """
    Finds all nodes SRC so there is a message from SRC to the given node

    :param node: the given node in the factor graph
    :return: a set of source nodes
    """
    return GetLink(
        TypedVariableLink(VariableNode('$SRC'), TypeNode('ConceptNode')),
        get_message_predicate(VariableNode('$SRC'), node))


# Probabilities

def has_probability(atom):
    """
    Checks that the atom contains probability value

    :param atom: the given atom
    :return: True if the atom contains a value for the probability key
    """
    if atom.get_value(key_probability()):
        return TV_TRUE
    return TV_FALSE


def set_variable_domain(variable, prob_atom, index):
    """
    Sets domain to the variable in factor graph.

    :param variable: variable in factor graph
    :param prob_atom: atom which contains joint probability table value
    :param index: position of the given variable in the joint probability table
    """
    tensor_value = prob_atom.get_value(key_probability())
    assert tensor_value, "Probability must be set for atom: " + str(prob_atom)
    tensor = tensor_value.value()
    domain = tensor.shape[index]

    current_domain_value = variable.get_value(key_domain())
    if not current_domain_value:
        variable.set_value(key_domain(), PtrValue(domain))
    else:
        assert current_domain_value.value() == domain


def set_factor_tensor(factor, variables, prob_atom):
    """
    Sets tensor for the given factor.
    Tensor is taken from  prob_atom.

    :param factor: factor in factor graph
    :param variables: initial variables
    :param prob_atom: atom which contains joint probability table value
    """

    arguments = [get_variable_node_name(v) for v in variables]
    # print("Set tensor arguments:", arguments)
    factor.set_value(key_arguments(), PtrValue(arguments))

    # Tensor indices must be reordered to be consistent with sorted variables names
    tensor_value = prob_atom.get_value(key_probability())
    assert tensor_value, "Probability must be set for atom: " + str(prob_atom)
    factor.set_value(key_tensor(), tensor_value)


def send_message_variable_factor(message, variable, factor, factors):
    domain = variable.get_value(key_domain()).value()
    message_value = np.ones(domain)

    for f in factors.get_out():
        if f != factor:
            msg_predicate = get_message_predicate(f, variable)
            msg_value = msg_predicate.get_value(key_message()).value()
            message_value = message_value * msg_value

    message.set_value(key_message(), PtrValue(message_value))
    print('send message (v-f):', variable.name, factor.name, message.get_value(key_message()).value())


def send_message_factor_variable(message, factor, variable):
    # print('send message (f-v):', factor.name, variable.name)
    arguments = factor.get_value(key_arguments()).value()
    tensor = factor.get_value(key_tensor()).value()

    for index, arg_name in reversed(list(enumerate(arguments))):
        if arg_name == variable.name:
            # This is the target variable. It's message is not used for tensor message multiplication.
            if index != 0:
                # Transpose tensor so the target variable axis becomes first
                axes = [index] + list(range(index))
                tensor = np.transpose(tensor, axes)
        else:
            v = ConceptNode(arg_name)
            # Note:
            # Do not create message predicate for the target variable.
            # It breaks send message variable factor rule.
            msg_predicate = get_message_predicate(v, factor)
            msg_value = msg_predicate.get_value(key_message())
            assert msg_value, "Value must be present for message: " + factor.name + "->" + arg_name
            msg = msg_value.value()
            tensor_index = len(tensor.shape) - 1
            tensor = np.tensordot(tensor, msg, axes=(tensor_index, 0))

    message.set_value(key_message(), PtrValue(tensor))
    print('send message (f-v):', factor.name, variable.name, message.get_value(key_message()).value())


# Utility methods

def dump_atomspace(atomspace):
    print("=== Dump AtomSpace Begin ===")
    for atom in atomspace:
        if not atom.incoming:
            print(str(atom))
    print("=== Dump AtomSpace End   ===")


def belief_propagation(atomspace):
    """
    Run Belief Propagation algorithm.

    :param atomspace: AtomSpace
    :return:
    """

    # Create factor graph
    res = execute_atom(atomspace, init_factor_graph_concept_node_rule())
    res = execute_atom(atomspace, init_factor_graph_implication_link_rule())

    # Send initial messages
    res = execute_atom(atomspace, send_message_variable_factor_rule())
    res = execute_atom(atomspace, send_message_factor_variable_rule())
    #

    # dump_atomspace(atomspace)

    res = execute_atom(atomspace, send_message_variable_factor_rule())
    res = execute_atom(atomspace, send_message_factor_variable_rule())
    #
    res = execute_atom(atomspace, send_message_variable_factor_rule())
    res = execute_atom(atomspace, send_message_factor_variable_rule())
    #
    # res = execute_atom(atomspace, send_message_variable_factor_rule())
    # res = execute_atom(atomspace, send_message_factor_variable_rule())

    # print(res)


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

def init_factor_graph_concept_node_rule():
    return BindLink(
        TypedVariableLink(VariableNode('$V'), TypeNode('ConceptNode')),
        EvaluationLink(
            GroundedPredicateNode('py: has_probability'),
            ListLink(
                VariableNode('$V'))),
        ExecutionOutputLink(
            GroundedSchemaNode('py: init_factor_graph_concept_node_formula'),
            ListLink(
                VariableNode('$V'))))


def init_factor_graph_concept_node_formula(v):
    # print('init_factor_graph_concept_node_formula', v.name)

    variable = get_variable_node(v)
    factor = get_factor_node([v])

    # generate factor graph predicates
    variable_predicate = get_variable_predicate(variable)
    factor_predicate = get_factor_predicate(factor)
    edge = get_edge_predicate(factor, variable)

    # set variable shape
    set_variable_domain(variable, v, 0)

    # set factor tensor
    set_factor_tensor(factor, [v], v)

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

def init_factor_graph_implication_link_rule():
    return BindLink(
        VariableList(
            TypedVariableLink(VariableNode('$V1'), TypeNode('ConceptNode')),
            TypedVariableLink(VariableNode('$V2'), TypeNode('ConceptNode'))),
        AndLink(
            # Preconditions
            EvaluationLink(
                GroundedPredicateNode('py: has_probability'),
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
                ImplicationLink(
                    VariableNode('$V1'),
                    VariableNode('$V2')),
                VariableNode('$V1'),
                VariableNode('$V2'))))


def init_factor_graph_implication_link_formula(I, v1, v2):
    # print('init_factor_graph_implication_link_formula', v1.name, v2.name)

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
    set_variable_domain(variable1, I, 0)
    set_variable_domain(variable2, I, 1)

    # # set factor tensor
    set_factor_tensor(factor, [v1, v2], I)

    return ListLink(
        variable_predicate_1,
        variable_predicate_2,
        factor_predicate,
        edge1,
        edge2
    )


# ; =====================================================================
# ; Send message Variable to Factor rule
# ;
# ; Evaluation
# ;    Predicate "variable"
# ;    V
# ; Evaluation
# ;    Predicate "factor"
# ;    F
# ; Evaluation
# ;    Predicate "edge"
# ;    List
# ;        Concept F
# ;        Concept V
# ; Absent
# ;    Evaluation
# ;        Predicate "message"
# ;        List
# ;            Concept V
# ;            Concept F
# ; |-
# ;
# ; Evaluation
# ;    Predicate "message"
# ;    List
# ;        Concept V
# ;        Concept F
# ;----------------------------------------------------------------------


def send_message_variable_factor_rule():
    return BindLink(
        VariableList(
            TypedVariableLink(VariableNode('$V'), TypeNode('ConceptNode')),
            TypedVariableLink(VariableNode('$F'), TypeNode('ConceptNode'))),
        AndLink(
            # Pattern clauses
            get_variable_predicate(VariableNode('$V')),
            get_factor_predicate(VariableNode('$F')),
            # Factor is always on the first place in edge
            get_edge_predicate(
                VariableNode('$F'),
                VariableNode('$V')),
            # Preconditions
            AbsentLink(
                get_message_predicate(
                    VariableNode('$V'),
                    VariableNode('$F'))),
            EqualLink(
                ArityLink(
                    BindLink(
                        TypedVariableLink(
                            VariableNode('$F1'),
                            TypeNode('ConceptNode')),
                        AndLink(
                            get_edge_predicate(VariableNode('$F1'), VariableNode('$V')),
                            NotLink(
                                EqualLink(
                                    VariableNode('$F1'),
                                    VariableNode('$F')))),
                        VariableNode('$F1'))),
                ArityLink(
                    BindLink(
                        TypedVariableLink(
                            VariableNode('$F1'),
                            TypeNode('ConceptNode')),
                        AndLink(
                            get_message_predicate(VariableNode('$F1'), VariableNode('$V')),
                            NotLink(
                                EqualLink(
                                    VariableNode('$F1'),
                                    VariableNode('$F')))),
                        VariableNode('$F1'))))),
        ExecutionOutputLink(
            GroundedSchemaNode('py: send_message_variable_factor_formula'),
            ListLink(
                get_message_predicate(
                    VariableNode('$V'),
                    VariableNode('$F')),
                VariableNode('$V'),
                VariableNode('$F'))))


def send_message_variable_factor_formula(message, variable, factor):
    # print('send_message_variable_factor_formula', variable.name, factor.name)
    sources = execute_atom(message.atomspace, get_messages_sources(variable))
    send_message_variable_factor(message, variable, factor, sources)
    return ListLink(
        message
    )


# ; =====================================================================
# ; Send message Factor to Variable rule
# ;
# ; Evaluation
# ;    Predicate "variable"
# ;    V
# ; Evaluation
# ;    Predicate "factor"
# ;    F
# ; Evaluation
# ;    Predicate "edge"
# ;    List
# ;        Concept F
# ;        Concept V
# ; Absent
# ;    Evaluation
# ;        Predicate "message"
# ;        List
# ;            Concept F
# ;            Concept V
# ; |-
# ;
# ; Evaluation
# ;    Predicate "message"
# ;    List
# ;        Concept F
# ;        Concept V
# ;----------------------------------------------------------------------


def send_message_factor_variable_rule():
    return BindLink(
        VariableList(
            TypedVariableLink(VariableNode('$V'), TypeNode('ConceptNode')),
            TypedVariableLink(VariableNode('$F'), TypeNode('ConceptNode'))),
        AndLink(
            # Pattern clauses
            get_variable_predicate(VariableNode('$V')),
            get_factor_predicate(VariableNode('$F')),
            # Factor is always on the first place in edge
            get_edge_predicate(
                VariableNode('$F'),
                VariableNode('$V')),
            # Preconditions
            AbsentLink(
                get_message_predicate(
                    VariableNode('$F'),
                    VariableNode('$V'))),
            EqualLink(
                ArityLink(
                    BindLink(
                        TypedVariableLink(
                            VariableNode('$V1'),
                            TypeNode('ConceptNode')),
                        AndLink(
                            get_edge_predicate(VariableNode('$F'), VariableNode('$V1')),
                            NotLink(
                                EqualLink(
                                    VariableNode('$V1'),
                                    VariableNode('$V')))),
                        VariableNode('$V1'))),
                ArityLink(
                    BindLink(
                        TypedVariableLink(
                            VariableNode('$V1'),
                            TypeNode('ConceptNode')),
                        AndLink(
                            get_message_predicate(VariableNode('$V1'), VariableNode('$F')),
                            NotLink(
                                EqualLink(
                                    VariableNode('$V1'),
                                    VariableNode('$V')))),
                        VariableNode('$V1'))))),
        ExecutionOutputLink(
            GroundedSchemaNode('py: send_message_factor_variable_formula'),
            ListLink(
                get_message_predicate(
                    VariableNode('$F'),
                    VariableNode('$V')),
                VariableNode('$F'),
                VariableNode('$V'))))


def send_message_factor_variable_formula(message, factor, variable):
    # print('send_message_factor_variable_formula', factor.name, variable.name)
    send_message_factor_variable(message, factor, variable)
    return ListLink(
        message
    )