from opencog.type_constructors import *
from opencog.atomspace import PtrValue
from opencog.bindlink import execute_atom

import numpy as np

TV_TRUE = TruthValue(1.0, 1.0)
TV_FALSE = TruthValue(0.0, 0.0)


# Keys

def key_probability():
    return PredicateNode("probability")


def key_factor():
    return PredicateNode("factor")


def key_variable():
    return PredicateNode("variable")


def key_edge():
    return PredicateNode("edge")


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


# Factor Graph

def get_variable_node(v):
    """
    Returns Variable node in factor graph
    The name of the variable node consists of 'Variable-' prefix and name of the original variable.

    :param v: original variable defined in Bayesian network
    :return: variable node in factor graph
    """
    name = 'Variable-' + v.name
    return ConceptNode(name)


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
    return BindLink(
        TypedVariableLink(
            VariableNode('$V'),
            TypeNode('ConceptNode')),
        EvaluationLink(
            GroundedPredicateNode('py: has_probability'),
            ListLink(
                VariableNode('$V'))),
        ExecutionOutputLink(
            GroundedSchemaNode('py: init_factor_graph_concept_node_formula'),
            ListLink(
                VariableNode('$V'))))


def init_factor_graph_concept_node_formula(v):
    print('init_factor_graph_concept_node_formula', v.name)

    variable = get_variable_node(v)
    factor = get_factor_node([v])

    # generate factor graph predicates
    variable_predicate = get_variable_predicate(variable)
    factor_predicate = get_factor_predicate(factor)
    edge = get_edge_predicate(factor, variable)

    # set variable shape
    # set_variable_shape_value(v, variable)

    # set factor tensor
    # set_factor_tensor(factor, [v], v)

    return ListLink(
        variable_predicate,
        factor_predicate,
        edge
    )


def belief_propagation(atomspace):
    """
    Run Belief Propagation algorithm.

    :param atomspace: AtomSpace
    :return:
    """
    res = execute_atom(atomspace, init_factor_graph_concept_node())
