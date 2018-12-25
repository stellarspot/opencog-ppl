from opencog.atomspace import AtomSpace, types

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *

from opencog.bindlink import bindlink
from opencog.bindlink import satisfaction_link

import numpy as np

atomspace = AtomSpace()
initialize_opencog(atomspace)


# Bayesian network graph

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


InheritanceLink(ConceptNode("TrueFalseValue"), ConceptNode("true"))
InheritanceLink(ConceptNode("TrueFalseValue"), ConceptNode("false"))

InheritanceLink(ConceptNode("Grass"), ConceptNode("wet"))
InheritanceLink(ConceptNode("Grass"), ConceptNode("dry"))

InheritanceLink(ConceptNode("Rain"), ConceptNode("TrueFalseValue"))
InheritanceLink(ConceptNode("WatsonGrass"), ConceptNode("Grass"))

probability_link([("Rain", "true")], 0.2)
probability_link([("Rain", "false")], 0.8)
# probability_link([("Sprinkler", "on")], 0.1)
# probability_link([("Sprinkler", "off")], 0.9)

probability_link([("Rain", "true"), ("WatsonGrass", "wet")], 1)
probability_link([("Rain", "true"), ("WatsonGrass", "dry")], 0)
probability_link([("Rain", "false"), ("WatsonGrass", "wet")], 0.2)
probability_link([("Rain", "false"), ("WatsonGrass", "dry")], 0.8)

# probability_link([("Rain", "true"), ("Sprinkler", "on"), ("HolmesGrass", "wet")], 1)
# probability_link([("Rain", "true"), ("Sprinkler", "on"), ("HolmesGrass", "dry")], 0)
# probability_link([("Rain", "true"), ("Sprinkler", "off"), ("HolmesGrass", "wet")], 0.9)
# probability_link([("Rain", "true"), ("Sprinkler", "off"), ("HolmesGrass", "dry")], 0.1)
# probability_link([("Rain", "false"), ("Sprinkler", "on"), ("HolmesGrass", "wet")], 1)
# probability_link([("Rain", "false"), ("Sprinkler", "on"), ("HolmesGrass", "dry")], 0)
# probability_link([("Rain", "false"), ("Sprinkler", "off"), ("HolmesGrass", "wet")], 0)
# probability_link([("Rain", "false"), ("Sprinkler", "off"), ("HolmesGrass", "dry")], 1)

EvaluationLink(
    PredicateNode("not-real-probability"),
    AssociativeLink(ConceptNode("test-not-include"), ConceptNode("value"))
)


def is_predicate(evalutation_link, predicate_name):
    return evalutation_link.out[0].name == predicate_name


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
#
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
KEY_VARIABLE_DOMAIN = "variable_domain"  # map[VariableName, ListOfVariableValues]
KEY_FACTOR_TENSOR = "factor_tensor"  # map[FactorName, FactorTensor]


def init_factor_graph(dict):
    evaluation_links = atomspace.get_atoms_by_type(types.EvaluationLink)
    factors = set()
    factor_edges = []
    factor_arguments = []
    factor_values = {}

    dict[KEY_VARIABLE_DOMAIN] = {}

    for link in evaluation_links:
        if not is_predicate(link, "probability"):
            continue
        variables, variable_value_key, probability = get_probability_variables(link)
        for variable in variables:
            init_variable_domain(variable, dict)

        factor_values[variable_value_key] = probability
        factor_name = 'factor-' + '-'.join(variables)
        if not factor_name in factors:
            variable_nodes = list(map(lambda name: ConceptNode(name), variables))
            factor_edges.extend(factor_graph_edges(factor_name, variable_nodes))
            factor_arguments.append(factor_arguments_list(factor_name, variable_nodes))
            factors.add(factor_name)

    # One probability rule has several factor edges: factor->variable
    factor_edges = list(set(factor_edges))
    dict[KEY_FACTOR_EDGES] = factor_edges
    dict[KEY_FACTOR_ARGUMENTS] = factor_arguments
    dict[KEY_FACTOR_VALUES] = factor_values
    dict[KEY_FACTOR_TENSOR] = {}
    init_factor_tensors(dict)
    print("factor tensors:", dict[KEY_FACTOR_TENSOR])


def init_variable_domain(variable, dict):
    domain_map = dict[KEY_VARIABLE_DOMAIN]
    if not variable in domain_map:
        domain = get_variable_domain(ConceptNode(variable))
        domain_map[variable] = domain


def init_factor_tensors(dict):
    factor_arguments = dict[KEY_FACTOR_ARGUMENTS]
    domains_map = dict[KEY_VARIABLE_DOMAIN]

    for factor_argument in factor_arguments:
        list_link = factor_argument.out[1]
        factor_node = list_link.out[0]
        variables_link = list_link.out[1]
        factor_name = factor_node.name

        variables = None
        if variables_link.type == types.ConceptNode:
            variables = [variables_link.name]
        elif variables_link.type == types.ListLink:
            variables = list(map(lambda node: node.name, variables_link.out))
        else:
            raise ValueError("Unknown node in factor-arguments-list predicate: " + factor_argument)

        init_factor_tensor(factor_name, variables, domains_map, dict)


# Put a factor tensor to the dict
def init_factor_tensor(factor_name, variables, domain_map, dict):
    factor_values = dict[KEY_FACTOR_VALUES]
    size = len(variables)
    indices = [0] * size
    indices[0] = -1
    bounds = list(map(lambda variable: len(domain_map[variable]), variables))
    tensor_values = []

    while (increment_indices(size, indices, bounds)):
        factor_value = get_factor_value(factor_name, variables, domain_map, indices, factor_values)
        tensor_values.append(factor_value)

    tensor_values = np.array(tensor_values).reshape(bounds)
    # print("tensor_values:", tensor_values)
    dict[KEY_FACTOR_TENSOR][factor_name] = tensor_values


def get_factor_value(factor_name, variables, domain_map, indices, factor_values):
    values = []
    for i in range(0, len(variables)):
        variable = variables[i]
        value_index = indices[i]
        value = domain_map[variable][value_index]
        values.append(value)
    key = get_variables_values_key(variables, values)
    value = factor_values[key]
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


# keys for messages FloatValue
KEY_MESSAGE_FACTOR_VARIABLE = "factor-variable"
KEY_MESSAGE_VARIABLE_FACTOR = "variable-factor"


# Edges are always from factor to variable
def get_edge_message(node_from, node_to, node_key):
    edge = factor_graph_edge(node_from, node_to)
    float_value = edge.get_value(node_key)

    if not float_value:
        return None
    return float_value.to_list()


def get_factor_variable_message(factor, variable):
    return get_edge_message(factor, variable, ConceptNode(KEY_MESSAGE_FACTOR_VARIABLE))


def get_variable_factor_message(variable, factor):
    return get_edge_message(factor, variable, ConceptNode(KEY_MESSAGE_VARIABLE_FACTOR))


def set_edge_message(node_from, node_to, node_key, message):
    # print("  set message: [", node_from.name, "->", node_to.name, "] ", node_key.name, message)
    edge = factor_graph_edge(node_from, node_to)
    edge.set_value(node_key, FloatValue(message))


def set_factor_variable_message(factor, variable, message):
    set_edge_message(factor, variable, ConceptNode(KEY_MESSAGE_FACTOR_VARIABLE), message)


def set_variable_factor_message(variable, factor, message):
    set_edge_message(factor, variable, ConceptNode(KEY_MESSAGE_VARIABLE_FACTOR), message)


def send_message_from_variable_to_factor(factor_graph_edges, variable, factor):
    print("send message(v->f): ", variable.name, "->", factor.name)
    message = get_variable_factor_message(variable, factor)

    if message:
        print("  message has been already sent:", message)
        return

    factor_edges = get_neighbour_factors(factor_graph_edges, variable, factor)

    # This is a leaf. Send initial message.
    if not factor_edges:
        print("  variable leaf")
        values = get_variable_domain(variable)
        domain_size = len(values)
        set_variable_factor_message(variable, factor, [1.0] * domain_size)


def send_message_from_factor_to_variable(factor_graph_edges, factor, variable, dict):
    print("send message(f->v): ", factor.name, "->", variable.name)
    message = get_factor_variable_message(factor, variable)

    if message:
        print("  message has been already sent:", message)
        return

    factor_tensor = dict[KEY_FACTOR_TENSOR][factor.name]
    factor_edges = get_neighbour_variables(factor_graph_edges, factor, variable)
    # This is a leaf. Send initial message.
    if not factor_edges:
        print("  factor leaf")
        set_factor_variable_message(factor, variable, factor_tensor.tolist())


def run_belief_propagation_algorithm():
    print("run_belief_propagation_algorithm")
    dict = {}
    init_factor_graph(dict)
    factor_graph_edges = dict[KEY_FACTOR_EDGES]
    factor_arguments = dict[KEY_FACTOR_ARGUMENTS]
    factor_values = dict[KEY_FACTOR_VALUES]
    # print("factor graph: ", factor_graph_edges)
    # print("factor arguments: ", factor_arguments)
    # print("factor values: ", factor_values)

    for step in range(0, 2):
        print()
        print("step: ", step)
        for edge in factor_graph_edges:
            list_link = edge.out[1]
            factor = list_link.out[0]
            variable = list_link.out[1]
            send_message_from_variable_to_factor(factor_graph_edges, variable, factor)
            send_message_from_factor_to_variable(factor_graph_edges, factor, variable, dict)


run_belief_propagation_algorithm()
