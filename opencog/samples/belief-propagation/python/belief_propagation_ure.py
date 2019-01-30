from opencog.utilities import initialize_opencog
from opencog.type_constructors import *
from opencog.bindlink import bindlink

from belief_propagation import *


def init_factor_graph():
    init_factor_graph_concept_node()
    init_factor_graph_implication_link()


def send_messages():
    send_message_variable_factor()
    send_message_factor_variable()


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
    print('init_factor_graph_concept_node_formula', v.name)

    variable = get_variable_node(v)
    factor = get_factor_node([v])

    # generate factor graph predicates
    variable_predicate = get_variable_predicate(variable)
    factor_predicate = get_factor_predicate(factor)
    edge = get_edge_predicate(factor, variable)

    # set variable shape
    set_variable_shape_value(v, variable)

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
                ImplicationLink(
                    VariableNode('$V1'),
                    VariableNode('$V2')),
                VariableNode('$V1'),
                VariableNode('$V2'))))
    bindlink(atomspace, bind_link)
    # print(bindlink(atomspace, bind_link))


def init_factor_graph_implication_link_formula(I, v1, v2):
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
    set_variable_shape_value(v1, variable1)
    set_variable_shape_value(v2, variable2)

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
                            VariableNode('$F'),
                            VariableNode('$V')),
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
            get_edge_predicate(
                VariableNode('$F'),
                VariableNode('$V'))
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
            get_edge_predicate(
                VariableNode('$F'),
                VariableNode('$V'))
        ),
        ExecutionOutputLink(
            GroundedSchemaNode('py: send_message_factor_variable_formula'),
            ListLink(
                VariableNode('$F'),
                VariableNode('$V'))))
    bindlink(atomspace, bind_link)
    # print(bindlink(atomspace, bind_link))


def send_message_factor_variable_formula(factor, variable):
    # print('send_message_factor_variable_formula', factor.name, variable.name)
    create_message_factor_variable(factor, variable)
    return ListLink()
