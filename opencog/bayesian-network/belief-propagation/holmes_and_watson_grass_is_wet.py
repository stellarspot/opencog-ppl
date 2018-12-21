from opencog.atomspace import AtomSpace, types

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *

from opencog.bindlink import bindlink

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
def factor_graph_edge(factor_name, variables):
    factor_node = ConceptNode(factor_name)
    factor_edges = []

    for variable in variables:
        list_link = atomspace.add_link(types.ListLink, [factor_node, variable])
        factor_edge = EvaluationLink(
            PredicateNode("graph-edge"),
            list_link
        )
        factor_edges.append(factor_edge)

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
KEY_VARIABLE_DOMAIN = "variable_domain"  # map[VariableName. ListOfVariableValues]


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
            factor_edges.extend(factor_graph_edge(factor_name, variable_nodes))
            factor_arguments.append(factor_arguments_list(factor_name, variable_nodes))
            factors.add(factor_name)

    # One probability rule has several factor edges: factor->variable
    factor_edges = list(set(factor_edges))
    dict[KEY_FACTOR_EDGES] = factor_edges
    dict[KEY_FACTOR_ARGUMENTS] = factor_arguments
    dict[KEY_FACTOR_VALUES] = factor_values
    init_factor_tensors(dict)


def init_variable_domain(variable, dict):
    domain_map = dict[KEY_VARIABLE_DOMAIN]
    if not variable in domain_map:
        # print("add domain for variable:", variable)
        domain = get_variable_domain(ConceptNode(variable))
        # print("variable domain:", domain)
        domain_map[variable] = domain


def init_factor_tensors(dict):
    print("init_factor_tensors")
    factor_arguments = dict[KEY_FACTOR_ARGUMENTS]
    # print("factor_arguments: ", factor_arguments)

    for factor_argument in factor_arguments:
        list_link = factor_argument.out[1]
        factor_node = list_link.out[0]
        variables_link = list_link.out[1]
        factor_name = factor_node.name
        print("factor name:", factor_name)

        variables = None
        if variables_link.type == types.ConceptNode:
            variables = [variables_link.name]
        elif variables_link.type == types.ListLink:
            variables = list(map(lambda node: node.name, variables_link.out))

        print("variables:", variables)


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
    edges = []
    for edge in factor_graph_edges:
        edge_factor_variable = get_edge_factor_variable(edge)
        edge_factor = edge_factor_variable[0]
        edge_variable = edge_factor_variable[1]

        if edge_variable.name == variable.name and edge_factor.name != exclude_factor.name:
            # print("  edge: ", edge_factor.name, "->", edge_variable.name)
            edges.append(edge)

    return edges


# message value is a comma separated string of values
# for example
# initial message: 1, 1
# where number of values is the domain of the variable or number of the variable evidences
# ordinary message: P(V=v1), P(V=v2), P(V=v3)
def generate_message(node_from, node_to, message):
    return EvaluationLink(
        PredicateNode("factor-graph-message"),
        ListLink(node_from, node_to, message))


# size of the variable domain
# or number of variable evidences
def get_initial_message_value(size):
    if size == 0:
        return ""

    message = "1"
    for i in range(1, size):
        message = message + ",1"

    return message


def send_message_from_variable_to_factor(factor_graph_edges, variable, factor):
    print("send message(v->f): ", variable.name, "->", factor.name)

    factor_edges = get_neighbour_factors(factor_graph_edges, variable, factor)

    # print(" income edges: ", factor_edges)

    # This is a leaf. Send initial message.
    if not factor_edges:
        print("variable leaf")
        values = get_variable_domain(variable)
        domain_size = len(values)
        # print("size: ", domain_size)
        # print("values: ", values)
        message_value = get_initial_message_value(domain_size)
        message = generate_message(variable, factor, ConceptNode(message_value))
        print("generated message: ", message)


def send_message_from_factor_to_variable(factor_graph_edges, factor, variable):
    print("send message(f->v): ", factor.name, "->", variable.name)

    factor_edges = get_neighbour_factors(factor_graph_edges, variable, factor)
    # This is a leaf. Send initial message.
    if not factor_edges:
        print("factor leaf")
        values = get_variable_domain(variable)
        print("values: ", values)
        # Calculate P(V=v1), P(V=v2)


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

    for edge in factor_graph_edges:
        list_link = edge.out[1]
        factor = list_link.out[0]
        variable = list_link.out[1]
        send_message_from_variable_to_factor(factor_graph_edges, variable, factor)
        send_message_from_factor_to_variable(factor_graph_edges, factor, variable)


run_belief_propagation_algorithm()
