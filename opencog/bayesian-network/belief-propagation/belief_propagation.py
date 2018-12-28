from opencog.atomspace import AtomSpace, types

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *

from opencog.bindlink import bindlink

import numpy as np

atomspace = AtomSpace()
initialize_opencog(atomspace)


# Belief Propagation Algorithm for Bayesian Network graph


# Probability predicate
#
# EvaluationLink (stv 0.2 1)
#   PredicateNode "probability"
#   AssociativeLink
#     Concept "Rain"
#     Concept "true"
#
# EvaluationLink (stv 1.0 1)
#   PredicateNode "probability"
#   ImplicationLink
#     AssociativeLink
#       Concept "Rain"
#       Concept "true"
#     AssociativeLink
#       Concept "WatsonGrass"
#       Concept "wet"

# Utility method to create a probability predicate:
#
# P(A=a|B=b,C=c) -> probability_link([B, b],[C, c], [A, a], probability)
def probability_link(name_value_tuples, probability):
    tv = TruthValue(probability, 1)
    size = len(name_value_tuples)
    if size == 1:
        name_value_tuple = name_value_tuples[0]
        link = EvaluationLink(
            PredicateNode("probability"),
            AssociativeLink(ConceptNode(name_value_tuple[0]), ConceptNode(name_value_tuple[1]))
        )
        link.tv = tv
        return link
    if size == 2:
        var1 = name_value_tuples[0]
        var2 = name_value_tuples[1]
        link = EvaluationLink(
            PredicateNode("probability"),
            ImplicationLink(
                AssociativeLink(ConceptNode(var1[0]), ConceptNode(var1[1])),
                AssociativeLink(ConceptNode(var2[0]), ConceptNode(var2[1]))))
        link.tv = tv
        return link

    implicants = []
    for implicant_tuple in name_value_tuples[:-1]:
        implicants.append(AssociativeLink(ConceptNode(implicant_tuple[0]), ConceptNode(implicant_tuple[1])))

    implicant = atomspace.add_link(types.AndLink, implicants)

    implicand_tuple = name_value_tuples[-1]
    implicand = AssociativeLink(ConceptNode(implicand_tuple[0]), ConceptNode(implicand_tuple[1]))

    link = EvaluationLink(
        PredicateNode("probability"),
        ImplicationLink(implicant, implicand)
    )
    link.tv = tv
    return link


EvaluationLink(
    PredicateNode("not-real-probability"),
    AssociativeLink(ConceptNode("test-not-include"), ConceptNode("value"))
)


def is_predicate(evalutation_link, predicate_name):
    return evalutation_link.out[0].name == predicate_name


# variables_values_key has format: Var1=value1|Var1=value1|...|VarN=valueN
#
# return (sorted list variable names, variables_values_key, probability)
def get_probability_variables(atom):
    variable_value_list = []
    evaluation_arg_1 = atom.out[1]

    if evaluation_arg_1.type == types.AssociativeLink:
        variable_value_list.append(get_probability_variable_value(evaluation_arg_1))
    elif evaluation_arg_1.type == types.ImplicationLink:
        implication_arg_0 = evaluation_arg_1.out[0]
        implication_arg_1 = evaluation_arg_1.out[1]
        if implication_arg_0.type == types.AssociativeLink:
            variable_value_list.append(get_probability_variable_value(implication_arg_0))
        elif implication_arg_0.type == types.ListLink:
            for and_implication in implication_arg_0.out:
                variable_value_list.append(get_probability_variable_value(and_implication))
        else:
            raise ValueError("Unknown atom in probability predicate: " + implication_arg_0.type)
        variable_value_list.append(get_probability_variable_value(implication_arg_1))
    else:
        raise ValueError("Unknown atom in probability predicate: " + evaluation_arg_1.type)

    # Sort variable value pairs by variable names
    variable_value_list.sort(key=lambda tuple: tuple[0])

    # list variables
    variables = list(map(lambda tuple: tuple[0], variable_value_list))

    # variables values key
    variable_value_key = map(lambda tuple: tuple[0] + "=" + tuple[1], variable_value_list)
    variable_value_key = "|".join(variable_value_key)

    # probability
    probability = atom.tv.mean

    return variables, variable_value_key, probability


# input list of variables and values: [V1, ..VN], [v1,..,vn]
# return: "V1=v1|...|Vn=vn"
def get_variables_values_key(variables, values):
    pairs = zip(variables, values)
    variables_values = list(map(lambda tuple: tuple[0] + "=" + tuple[1], pairs))
    key = "|".join(variables_values)
    return key


#     AssociativeLink
#       Concept "WatsonGrass"
#       Concept "wet"
def get_probability_variable_value(atom):
    return atom.out[0].name, atom.out[1].name


# Graph Edge predicate
#
# EvaluationLink
#   PredicateNode "graph-edge"
#   ListLink Factor Variable
def factor_graph_edge(factor, variable):
    return EvaluationLink(
        PredicateNode("graph-edge"),
        ListLink(factor, variable))


# generate edges for the given factor and variables list
def factor_graph_edges(factor_name, variables):
    factor_node = ConceptNode(factor_name)
    factor_edges = []

    for variable in variables:
        factor_edges.append(factor_graph_edge(factor_node, variable))
    return factor_edges


# Factor Arguments List predicate
#
# EvaluationLink
#   PredicateNode "factor-arguments-list"
#   ListLink
#     Factor
#     Variable
#
# EvaluationLink
#   PredicateNode "factor-arguments-list"
#   ListLink
#     Factor
#     ListLink
#       Variable1
#       VariableN
def factor_arguments_list(factor_name, variables):
    list = None

    if len(variables) == 1:
        list = variables[0]
    else:
        list = atomspace.add_link(types.ListLink, variables)

    return EvaluationLink(
        PredicateNode("factor-arguments-list"),
        ListLink(ConceptNode(factor_name), list)
    )


# dict keys for init_factor_graph:
KEY_FACTOR_EDGES = "factor_edges"
KEY_FACTOR_ARGUMENTS = "factor_arguments"
KEY_FACTOR_VALUES = "factor_values"
KEY_FACTOR_VARIABLES = "factor_variables"
KEY_VARIABLE_DOMAIN = "variable_domain"  # map[VariableName, ListOfVariableValues]
KEY_FACTOR_TENSOR_VALUES = "factor_tensor_values"  # map[FactorName, FactorTensor]
KEY_FACTOR_TENSOR_BOUNDS = "factor_tensor_bounds"  # map[FactorName, FactorTensor]


def init_factor_graph(dict):
    evaluation_links = atomspace.get_atoms_by_type(types.EvaluationLink)
    factors = set()
    factor_edges = []

    for link in evaluation_links:
        if not is_predicate(link, "probability"):
            continue
        variables, variable_value_key, probability = get_probability_variables(link)
        for variable_name in variables:
            init_variable(variable_name)

        factor_name = 'Factor-' + '-'.join(variables)
        factor = ConceptNode(factor_name)
        set_factor_probability(factor, variable_value_key, probability)
        if not factor_name in factors:
            init_factor(factor, variables)
            variable_nodes = list(map(lambda name: ConceptNode(name), variables))
            factor_edges.extend(factor_graph_edges(factor_name, variable_nodes))
            factors.add(factor_name)

    for factor_name in factors:
        init_factor_tensor(ConceptNode(factor_name))

    # One probability rule has several factor edges: factor->variable
    factor_edges = list(set(factor_edges))
    dict[KEY_FACTOR_EDGES] = factor_edges


# Init variable domain values
def init_variable(variable_name):
    variable = ConceptNode(variable_name)
    domain = get_variable_domain_value(variable)
    if not domain:
        domain = get_variable_domain(variable)
        variable.set_value(ConceptNode(KEY_VARIABLE_DOMAIN), StringValue(domain))


def get_variable_domain_value(variable):
    string_value = variable.get_value(ConceptNode(KEY_VARIABLE_DOMAIN))
    if not string_value:
        return None
    return string_value.to_list()


def init_factor(factor, variable_names):
    factor.set_value(ConceptNode(KEY_FACTOR_ARGUMENTS), StringValue(variable_names))


def set_factor_probability(factor, variable_value_key, probability):
    factor.set_value(ConceptNode(variable_value_key), FloatValue(probability))


def get_factor_probability(factor, variable_value_key):
    return factor.get_value(ConceptNode(variable_value_key)).to_list()[0]


def get_factor_arguments(factor):
    return factor.get_value(ConceptNode(KEY_FACTOR_ARGUMENTS)).to_list()


def init_factor_probability_map(factor):
    pass


def init_factor_tensor(factor):
    arguments = get_factor_arguments(factor)

    size = len(arguments)
    indices = [0] * size
    indices[0] = -1

    domain_map = {}
    bounds = []
    for variable_name in arguments:
        domain = get_variable_domain_value(ConceptNode(variable_name))
        bounds.append(len(domain))
        domain_map[variable_name] = domain

    # factor = ConceptNode(factor_name)
    tensor_values = []

    while increment_indices(size, indices, bounds):
        factor_value = get_factor_probability_with_indices(factor, indices)
        tensor_values.append(factor_value)

    factor.set_value(ConceptNode(KEY_FACTOR_TENSOR_BOUNDS), FloatValue(bounds))
    factor.set_value(ConceptNode(KEY_FACTOR_TENSOR_VALUES), FloatValue(tensor_values))


def get_factor_probability_with_indices(factor, indices):
    arguments = get_factor_arguments(factor)
    values = []
    for i in range(0, len(arguments)):
        variable_name = arguments[i]
        value_index = indices[i]
        domain = get_variable_domain_value(ConceptNode(variable_name))
        value = domain[value_index]
        values.append(value)

    key = get_variables_values_key(arguments, values)
    value = get_factor_probability(factor, key)
    return value


# Iterate over all variable values from all domains
def increment_indices(size, indices, bounds):
    for i in range(0, len(indices)):
        indices[i] = indices[i] + 1
        if (indices[i] < bounds[i]):
            return True
        else:
            indices[i] = 0
    return False


def get_variable_domain(variable):
    # TBD: check also number of evidences

    bind_link = BindLink(
        VariableList(
            VariableNode("$type"),
            VariableNode("$value")),
        AndLink(
            InheritanceLink(
                variable,
                VariableNode("$type")),
            InheritanceLink(
                VariableNode("$type"),
                VariableNode("$value"))
        ),
        VariableNode("$value"))

    values_link = bindlink(atomspace, bind_link)
    values = list(map(lambda node: node.name, values_link.out))
    values.sort()

    return values


def get_edge_factor_variable(edge):
    list_link = edge.out[1]
    return (list_link.out[0], list_link.out[1])


def get_neighbour_factors(factor_graph_edges, variable, exclude_factor):
    filter = lambda factor_name, variable_name: \
        variable_name == variable.name and factor_name != exclude_factor.name
    edges = get_factor_graph_neighbours(factor_graph_edges, filter)
    return edges


def get_neighbour_variables(factor_graph_edges, factor, exclude_variable):
    filter = lambda factor_name, variable_name: \
        variable_name != exclude_variable.name and factor_name == factor.name
    edges = get_factor_graph_neighbours(factor_graph_edges, filter)
    return edges


def get_factor_graph_neighbours(factor_graph_edges, filter):
    edges = []
    for edge in factor_graph_edges:
        edge_factor_variable = get_edge_factor_variable(edge)
        edge_factor = edge_factor_variable[0]
        edge_variable = edge_factor_variable[1]

        if filter(edge_factor.name, edge_variable.name):
            edges.append(edge)

    return edges


# keys for FloatValue messages
KEY_MESSAGE_FACTOR_VARIABLE = "factor-variable"
KEY_MESSAGE_VARIABLE_FACTOR = "variable-factor"


# Edges are always from factor to variable
def get_edge_message(edge, node_key):
    float_value = edge.get_value(node_key)

    if not float_value:
        return None
    return float_value.to_list()


def get_variable_factor_edge_message(node_from, node_to, node_key):
    return get_edge_message(factor_graph_edge(node_from, node_to), node_key)


def get_factor_variable_message(factor, variable):
    return get_variable_factor_edge_message(factor, variable, ConceptNode(KEY_MESSAGE_FACTOR_VARIABLE))


def get_variable_factor_message(variable, factor):
    return get_variable_factor_edge_message(factor, variable, ConceptNode(KEY_MESSAGE_VARIABLE_FACTOR))


def set_edge_message(node_from, node_to, node_key, message):
    print("  set message: [", node_from.name, "->", node_to.name, "] ", node_key.name, message)
    edge = factor_graph_edge(node_from, node_to)
    edge.set_value(node_key, FloatValue(message))


def set_factor_variable_message(factor, variable, message):
    set_edge_message(factor, variable, ConceptNode(KEY_MESSAGE_FACTOR_VARIABLE), message)


def set_variable_factor_message(variable, factor, message):
    set_edge_message(factor, variable, ConceptNode(KEY_MESSAGE_VARIABLE_FACTOR), message)


def componentwise_messages_multiplication(messages, size):
    # print("  messages:", messages)
    message = np.array([1.0] * size)
    arrays = list(map(lambda msg: np.array(msg), messages))
    for msg in arrays:
        message = message * msg

    return message.tolist()


def tensor_messages_multiplication(factor, messages):
    bounds = factor.get_value(ConceptNode(KEY_FACTOR_TENSOR_BOUNDS)).to_list()
    bounds = list(map(lambda v: int(v), bounds))
    tensor_values = factor.get_value(ConceptNode(KEY_FACTOR_TENSOR_VALUES)).to_list()

    tensor = np.array(tensor_values).reshape(bounds)

    t = tensor
    for i in range(0, len(messages)):
        msg = messages[i]
        if not msg:
            continue
        v = np.array(msg)
        t = np.tensordot(t, v, axes=(i, 0))

    return t.tolist()


# Return True if message has been sent
def send_message_from_variable_to_factor(factor_graph_edges, variable, factor):
    print("send message(v->f): ", variable.name, "->", factor.name)
    message = get_variable_factor_message(variable, factor)

    if message:
        print("  message has been already sent:", message)
        return True

    factor_edges = get_neighbour_factors(factor_graph_edges, variable, factor)

    values = get_variable_domain(variable)
    domain_size = len(values)

    if not factor_edges:
        # This is a leaf. Send initial message.
        print("  send initial message: leaf")
        set_variable_factor_message(variable, factor, [1.0] * domain_size)
    else:
        messages = []
        for edge in factor_edges:
            msg = get_edge_message(edge, ConceptNode(KEY_MESSAGE_FACTOR_VARIABLE))
            if not msg:
                return False
            messages.append(msg)
        result_message = componentwise_messages_multiplication(messages, domain_size)
        set_variable_factor_message(variable, factor, result_message)
        return True

    return False


# Return True if message has been sent
def send_message_from_factor_to_variable(factor_graph_edges, factor, variable, dict):
    print("send message(f->v): ", factor.name, "->", variable.name)
    message = get_factor_variable_message(factor, variable)

    if message:
        print("  message has been already sent:", message)
        return True

    factor_edges = get_neighbour_variables(factor_graph_edges, factor, variable)
    if not factor_edges:
        # This is a leaf. Send initial message.
        print("  send initial message: leaf")
        factor_tensor_values = factor.get_value(ConceptNode(KEY_FACTOR_TENSOR_VALUES))
        set_factor_variable_message(factor, variable, factor_tensor_values.to_list())
    else:
        variable_name = variable.name
        factor_arguments = get_factor_arguments(factor)
        messages = []

        for arg_name in factor_arguments:
            if arg_name == variable_name:
                messages.append(None)
                continue
            msg = get_variable_factor_message(ConceptNode(arg_name), factor)
            if not msg:
                return False
            messages.append(msg)

        result_message = tensor_messages_multiplication(factor, messages)
        set_factor_variable_message(factor, variable, result_message)
        return True

    return False


def run_belief_propagation_algorithm():
    print("run_belief_propagation_algorithm")
    dict = {}
    init_factor_graph(dict)
    factor_graph_edges = dict[KEY_FACTOR_EDGES]

    step = 0
    while True:
        step += 1
        print()
        print("step: ", step)
        all_messages_are_sent = True
        for edge in factor_graph_edges:
            list_link = edge.out[1]
            factor = list_link.out[0]
            variable = list_link.out[1]
            # msg[variable->factor]
            is_message_sent = send_message_from_variable_to_factor(factor_graph_edges, variable, factor)
            all_messages_are_sent = all_messages_are_sent and is_message_sent
            # msg[factor->variable]
            is_message_sent = send_message_from_factor_to_variable(factor_graph_edges, factor, variable, dict)
            all_messages_are_sent = all_messages_are_sent and is_message_sent
        if all_messages_are_sent:
            print("all messages are sent")
            break

# run_belief_propagation_algorithm()
