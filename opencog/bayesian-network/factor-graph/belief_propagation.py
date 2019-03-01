from opencog.type_constructors import *
from opencog.atomspace import PtrValue
from opencog.bindlink import execute_atom
from opencog.ure import ForwardChainer

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


def key_evidence():
    return PredicateNode("evidence")


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


def set_variable_domain(variable, v, joint_table_atom, index):
    """
    Sets domain to the variable in factor graph.
    The domain of the variable is 1 if the evidence is set to the given v.
    Otherwise the domain of the variable is just dimension in the joint probability table
    where the variable has the given index.

    :param variable: variable in factor graph
    :param v: original variable in the bayesian network
    :param joint_table_atom: atom which contains joint probability table value
    :param index: position of the given variable in the joint probability table
    """
    tensor_value = joint_table_atom.get_value(key_probability())
    assert tensor_value, "Probability must be set for atom: " + str(joint_table_atom)
    tensor = tensor_value.value()

    evidence_index_value = v.get_value(key_evidence())
    if evidence_index_value:
        domain = 1
    else:
        domain = tensor.shape[index]

    # print("variable:", variable.name, "domain:", domain)

    current_domain_value = variable.get_value(key_domain())
    if not current_domain_value:
        variable.set_value(key_domain(), PtrValue(domain))
    else:
        assert current_domain_value.value() == domain, "Teh variable domain should be consistent " \
                                                       "with already present domain"


def set_factor_tensor(factor, variables, joint_table_atom):
    """
    Sets tensor for the given factor.
    Tensor is taken from  joint probability table.
    If a given variable has an evidence index, only evidence part of the joint table is taken.

    :param factor: factor in factor graph
    :param variables: original variables from the bayesian network
    :param joint_table_atom: atom which contains joint probability table value
    """

    arguments = [get_variable_node_name(v) for v in variables]
    factor.set_value(key_arguments(), PtrValue(arguments))

    tensor_value = joint_table_atom.get_value(key_probability())
    assert tensor_value, "Probability must be set for atom: " + str(joint_table_atom)

    tensor = tensor_value.value()

    for index, v in enumerate(variables):
        evidence_index_value = v.get_value(key_evidence())
        if evidence_index_value:
            evidence_index = evidence_index_value.value()
            tensor = np.take(tensor, [evidence_index], index)

    # print("factor:", factor.name, "tensor:", tensor)
    factor.set_value(key_tensor(), PtrValue(tensor))


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


def calculate_marginals(internal_atomspace):
    factors_link = GetLink(
        TypedVariableLink(VariableNode('$F'), TypeNode('ConceptNode')),
        get_factor_predicate(VariableNode('$F'))
    )

    factors = execute_atom(internal_atomspace, factors_link)

    for factor in factors.get_out():
        # print("factor:", factor.name)

        variables_link = GetLink(
            TypedVariableLink(VariableNode('$V'), TypeNode('ConceptNode')),
            get_edge_predicate(factor, VariableNode('$V'))
        )
        variables = execute_atom(internal_atomspace, variables_link)

        for variable in variables.get_out():
            # print("variable:", variable.name)

            # Multiply one in and one out message for each
            message_variable_factor = get_message_predicate(variable, factor)
            message_factor_variable = get_message_predicate(factor, variable)

            message_in = message_variable_factor.get_value(key_message()).value()
            message_out = message_factor_variable.get_value(key_message()).value()

            # print("  message1:", message_in)
            # print("  message2:", message_out)
            marginalization = np.dot(message_in, message_out)
            # print("marginalization:", marginalization)
            return marginalization

            break
        break


# Utility methods

def dump_atomspace(check_atomspace):
    print("=== Dump AtomSpace Begin ===")
    for atom in check_atomspace:
        if not atom.incoming:
            print(str(atom))
    print("=== Dump AtomSpace End   ===")


# URE

def run_forward_chainer(internal_atomspace):
    send_messages_rbs = ConceptNode("send-messages-rule-base")

    send_message_variable_factor = DefinedSchemaNode("send-message-variable-factor-rule")
    send_message_factor_variable = DefinedSchemaNode("send-message-factor-variable-rule")

    DefineLink(
        send_message_variable_factor,
        send_message_variable_factor_rule())

    DefineLink(
        send_message_factor_variable,
        send_message_factor_variable_rule())

    MemberLink(
        send_message_variable_factor,
        send_messages_rbs
    )

    MemberLink(
        send_message_factor_variable,
        send_messages_rbs
    )

    # Set URE maximum-iterations
    from opencog.scheme_wrapper import scheme_eval

    execute_code = \
        '''
        (use-modules (opencog rule-engine))
        (ure-set-num-parameter (ConceptNode "{}") "URE:maximum-iterations" 50)
        '''.format(send_messages_rbs.name)

    scheme_eval(internal_atomspace, execute_code)

    EvaluationLink(
        PredicateNode("URE:FC:retry-exhausted-sources"),
        send_messages_rbs
    ).tv = TruthValue(1, 1)

    chainer = ForwardChainer(internal_atomspace,
                             send_messages_rbs,
                             get_edge_predicate(VariableNode("$F"), VariableNode("$V")),
                             VariableList(
                                 TypedVariableLink(VariableNode("$F"), TypeNode("ConceptNode")),
                                 TypedVariableLink(VariableNode("$V"), TypeNode("ConceptNode"))))

    chainer.do_chain()
    # results = chainer.get_results()
    # print(results)


def belief_propagation(internal_atomspace):
    """
    Run Belief Propagation algorithm to calculate joint distribution marginalization over variables which are not
    listed as evidences.

    :param internal_atomspace: atomspace where factor graph is created
    :return: marginalization over free variables
    """

    # Create factor graph
    execute_atom(internal_atomspace, init_factor_graph_concept_node_rule())
    execute_atom(internal_atomspace, init_factor_graph_implication_link_rule())
    execute_atom(internal_atomspace, init_factor_graph_implication_link_product_rule())

    # Run Forward Chainer
    run_forward_chainer(internal_atomspace)

    # Return marginalization over free variables
    return calculate_marginals(internal_atomspace)


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
    set_variable_domain(variable, v, v, 0)

    # set factor tensor
    set_factor_tensor(factor, [v], v)

    return ListLink(
        variable_predicate,
        factor_predicate,
        edge)


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
    set_variable_domain(variable1, v1, I, 0)
    set_variable_domain(variable2, v2, I, 1)

    # # set factor tensor
    set_factor_tensor(factor, [v1, v2], I)

    return ListLink(
        variable_predicate_1,
        variable_predicate_2,
        factor_predicate,
        edge1,
        edge2)


# ; =====================================================================
# ; Implication Product to Variable rule
# ;
# ; Implication
# ;   List
# ;        As
# ;   B
# ; |-
# ; Evaluation
# ;    Predicate "factor"
# ;    Concept "Factor-As-B"
# ;
# ; Evaluation
# ;    Predicate "variable"
# ;    Concept "Variable-As"
# ;
# ; Evaluation
# ;    Predicate "edge"
# ;    List
# ;        Concept "Factor-As-B"
# ;        Concept "Variable-As"
# ;----------------------------------------------------------------------

def init_factor_graph_implication_link_product_rule():
    return BindLink(
        VariableList(
            GlobNode("$Vs"),
            TypedVariableLink(VariableNode('$V'), TypeNode('ConceptNode'))),
        AndLink(
            # Preconditions
            EvaluationLink(
                GroundedPredicateNode('py: has_probability'),
                ListLink(
                    ImplicationLink(
                        ListLink(
                            GlobNode('$Vs')),
                        VariableNode('$V')))),
            # Pattern clauses
            ImplicationLink(
                ListLink(
                    GlobNode('$Vs')),
                VariableNode('$V'))),
        ExecutionOutputLink(
            GroundedSchemaNode('py: init_factor_graph_implication_link_product_formula'),
            ListLink(
                ImplicationLink(
                    ListLink(
                        GlobNode('$Vs')),
                    VariableNode('$V')),
                VariableNode('$V'))))


def init_factor_graph_implication_link_product_formula(I, v):
    # print('init_factor_graph_implication_link_product_rule', v.name)
    list_link = I.get_out()
    globs = list_link[0].get_out()
    vs = [var for var in globs]
    vs.append(v)

    factor = get_factor_node(vs)
    set_factor_tensor(factor, vs, I)

    result = [get_factor_predicate(factor)]

    for index, var in enumerate(vs):
        variable = get_variable_node(var)
        set_variable_domain(variable, var, I, index)
        result.append(get_variable_predicate(variable))
        result.append(get_edge_predicate(factor, variable))

    return ListLink(result)


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
