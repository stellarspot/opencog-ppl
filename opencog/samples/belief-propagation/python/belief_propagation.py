import numpy as np

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *
from opencog.bindlink import bindlink

# AtomSpace Initialization
atomspace = AtomSpace()
initialize_opencog(atomspace)

from belief_propagation_constants import *


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
        variable)


def get_factor_predicate(factor):
    return EvaluationLink(
        FACTOR_KEY,
        factor)


def get_edge_predicate(factor, variable):
    """
    Create an edge for the given factor and variable in the factor graph.
    Note, that the factor must always be the first argument and the variable the second.
    There are no edges from variables to factors.

    :param factor: factor in factor factor graph
    :param variable: variable in factor factor graph
    :return: edge predicate for the given factor and variable
    """
    return EvaluationLink(
        EDGE_KEY,
        ListLink(
            factor,
            variable))


def set_variable_shape_value(v, variable):
    shape = v.get_value(SHAPE_KEY)
    if shape:
        variable.set_value(SHAPE_KEY, shape)


def set_factor_tensor(factor, variables, dv_atom):
    """
    Sets shape and tensor for the given factor.
    Shape is a list of shapes of given variables.
    Tensor is set in dv_atom.

    :param factor: factor in factor graph
    :param variables: initial variables
    :param dv_atom: atom which contains dv value
    """

    # print('set factor tensor:', factor.name)
    variables.sort()

    shape = list(map(lambda v: get_variable_shape(v), variables))
    # print('factor shape:', shape)
    factor.set_value(SHAPE_KEY, FloatValue(shape))

    tensor = get_factor_tensor(dv_atom)
    # print('tensor: ', tensor)
    factor.set_value(CDV_KEY, FloatValue(tensor))


def get_neighbors_factors(variable, exclude_factor):
    """
    Find all but exclude_factor factors which are connected with the given variable.

    :param variable: variable in factor graph
    :param exclude_factor: the factor that must must be excluded from the result.
    :return: the SetLink which contains a list of factors except the given factor.
    """
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


def get_neighbors_variables(factor, exclude_variable):
    """
    Find all but exclude_variable variables which are connected with the given factor.

    :param factor: factor in factor graph
    :param exclude_variable: the variable that must must be excluded from the result.
    :return: the SetLink which contains a list of variables except the given variable.
    """
    bind_link = BindLink(
        VariableNode('$V'),
        AndLink(
            get_variable_predicate(
                VariableNode('$V')),
            get_edge_predicate(
                factor,
                VariableNode('$V')),
            NotLink(
                EqualLink(
                    exclude_variable,
                    VariableNode('$V')))),
        VariableNode('$V'))

    factors_link = bindlink(atomspace, bind_link)
    return factors_link


def get_all_neighbors_variables(factor):
    """
    Find all variables which are connected with the given factor.
    This method is used for Factor tensor message multiplication to skip position
    of the variable the message is sent to.

    :param factor: factor in factor graph
    :return: the SetLink which contains a list of all variables connected to the factor.
    """
    bind_link = BindLink(
        VariableNode('$V'),
        AndLink(
            get_variable_predicate(
                VariableNode('$V')),
            get_edge_predicate(
                factor,
                VariableNode('$V'))),
        VariableNode('$V'))

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

    edge = get_edge_predicate(factor, variable)
    # print('edge:', edge)

    if has_value(edge, MESSAGE_VARIABLE_FACTOR_KEY):
        # print('HAS_VALUE')
        return TV_FALSE

    factors = get_neighbors_factors(variable, factor).out

    if not factors:
        return TV_TRUE
    else:
        for f in factors:
            edge = get_edge_predicate(f, variable)
            if not has_value(edge, MESSAGE_FACTOR_VARIABLE_KEY):
                return TV_FALSE

    return TV_TRUE


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

    # print('can_send_message_factor_variable', factor.name, variable.name)

    edge = get_edge_predicate(factor, variable)

    if has_value(edge, MESSAGE_FACTOR_VARIABLE_KEY):
        return TV_FALSE

    variables = get_neighbors_variables(factor, variable).out

    if not variables:
        return TV_TRUE
    else:
        for v in variables:
            edge = get_edge_predicate(factor, v)
            if not has_value(edge, MESSAGE_VARIABLE_FACTOR_KEY):
                return TV_FALSE

    return TV_TRUE


def get_variable_shape(variable):
    """
    Return the variable dimension from shape value as int

    :param variable: variable in factor factor graph
    :return: dimension of the variable
    """

    shape = variable.get_value(SHAPE_KEY)
    assert shape, 'Shape must be set for variable: ' + variable.name
    return int(shape.to_list()[0])


def get_factor_tensor(atom):
    """
    Return the tensor which is set as DV value for the given atom.

    :param atom: atom which contains DV
    :return: factor tensor
    """

    tensor_value = atom.get_value(CDV_KEY)
    assert tensor_value, 'Tensor must be set for atom: ' + str(atom)
    return tensor_value.to_list()


def get_factor_shape(factor):
    """
    Returns dimensions of the factor arguments

    :param factor: factor in factor factor graph
    :return: dimensions of the factor arguments
    """

    shape = factor.get_value(SHAPE_KEY)
    assert shape, 'Shape must be set for factor: ' + factor.name

    return [int(x) for x in shape.to_list()]


def get_initial_message_variable(variable):
    """
    :param variable: variable in factor factor graph
    :return: [1.0] * variable shape
    """

    return [1.0] * get_variable_shape(variable)


def get_initial_message_factor(factor):
    """
    :param factor: factor in factor graph
    :return: initial tensor from the factor
    """
    # TBD use get_tensor()
    tensor = factor.get_value(CDV_KEY)
    assert tensor, 'Tensor must be set for factor: ' + factor.name
    return tensor.to_list()


def get_message_componentwise_multiplication(messages, size):
    """
    Multiplies the given list of messages componentwise.
    Each message is python list of floats with the same size.

    :param messages: list of incoming messages
    :param size: size of outcome message
    :return: outcome message
    """

    message = np.array([1.0] * size)
    arrays = list(map(lambda msg: np.array(msg), messages))
    for msg in arrays:
        message = message * msg

    return message.tolist()


def get_message_tensor_multiplication(factor, messages):
    """
    Multiplies the factor tensor to incoming messages to get the outcome message.
    Each message is a list of float values or None in case it is a position
    of the variable the messages is sent to.

    :param factor: factor in factor graph
    :param messages: list of incoming messages contained None in the position of the target variable.
    :return:
    """
    bounds = get_factor_shape(factor)
    tensor_values = get_factor_tensor(factor)
    tensor = np.array(tensor_values).reshape(bounds)

    t = tensor
    for i in range(0, len(messages)):
        msg = messages[i]
        if not msg:
            continue
        v = np.array(msg)
        t = np.tensordot(t, v, axes=(i, 0))

    return t.tolist()


def set_message_edge(edge, key, message):
    """
    Sets the message to graph edge.

    :param edge: edge in factor graph
    :param key: key for the message,
                either MESSAGE_VARIABLE_FACTOR_KEY or MESSAGE_FACTOR_VARIABLE_KEY
    :param message: python list of float values
    """

    value = FloatValue(message)
    edge.set_value(key, value)


def create_message_variable_factor(variable, factor):
    """
    Creates a message from the variable to factor and set it to edge.

    :param variable: variable in factor factor graph
    :param factor: factor in factor graph
    """
    factors = get_neighbors_factors(variable, factor).out
    msg = None

    if not factors:
        edge = get_edge_predicate(factor, variable)
        msg = get_initial_message_variable(variable)
    else:
        messages = []
        for f in factors:
            edge = get_edge_predicate(f, variable)
            msg_value = edge.get_value(MESSAGE_FACTOR_VARIABLE_KEY)
            assert msg_value, 'Message must be set for edge:' + f.name + '->' + variable.name
            m = float_value_to_list(msg_value)
            messages.append(m)

        shape = get_variable_shape(variable)
        msg = get_message_componentwise_multiplication(messages, shape)

    if msg:
        print('message (v->f):', variable.name, factor.name, msg)
        set_message_edge(edge, MESSAGE_VARIABLE_FACTOR_KEY, msg)


def create_message_factor_variable(factor, variable):
    """
    Creates a message from the factor to variable and set it to edge.

    :param factor: factor in factor graph
    :param variable: variable in factor graph
    """
    variables = get_all_neighbors_variables(factor).out
    msg = None

    # variables consists at least with one variable which is an argumnet
    # of the given factor
    if len(variables) == 1:
        edge = get_edge_predicate(factor, variable)
        msg = get_initial_message_factor(factor)
    else:
        # Variables must be sorted to be consistent with the factor shape
        sorted(variables, key=lambda v: v.name)
        messages = []
        for v in variables:
            edge = get_edge_predicate(factor, v)
            msg_value = edge.get_value(MESSAGE_VARIABLE_FACTOR_KEY)
            if not msg_value:
                messages.append(None)
            else:
                m = float_value_to_list(msg_value)
                messages.append(m)

        msg = get_message_tensor_multiplication(factor, messages)

    if msg:
        print('message (f->v):', factor.name, variable.name, msg)
        set_message_edge(edge, MESSAGE_FACTOR_VARIABLE_KEY, msg)


# Utility methods

def show_atomspace():
    print('--- AtomSpace Dump---')
    for atom in atomspace:
        print(atom)
    print('---------------------')


def show_edges():
    bind_link = BindLink(
        VariableList(
            TypedVariableLink(
                VariableNode('$F'),
                TypeNode('ConceptNode')),
            TypedVariableLink(
                VariableNode('$V'),
                TypeNode('ConceptNode'))),
        get_edge_predicate(
            VariableNode('$F'),
            VariableNode('$V')
        ),
        get_edge_predicate(
            VariableNode('$F'),
            VariableNode('$V')
        )
    )
    print(bindlink(atomspace, bind_link))


# Belief Propagation Utility methods

def bool_to_tv(b):
    if not b:
        return TV_FALSE
    return TV_TRUE


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
        return TV_TRUE
    return TV_FALSE


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
    print()
