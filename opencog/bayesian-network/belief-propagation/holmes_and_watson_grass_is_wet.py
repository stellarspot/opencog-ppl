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


# probability_link: predicate 'probability'
def get_probability_variables(atom):
    variables = []
    if atom.type == types.EvaluationLink:
        variables.extend(get_probability_variables(atom.out[1]))
    elif atom.type == types.AssociativeLink:
        variables.append(atom.out[0])
    elif atom.type == types.ImplicationLink:
        variables.extend(get_probability_variables(atom.out[0]))
        variables.extend(get_probability_variables(atom.out[1]))
    elif atom.type == types.AndLink:
        for a in atom.out:
            variables.extend(get_probability_variables(a))
    return variables


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
#     Variable1
#     VariableN
def factor_arguments_list(factor_name, variables):
    list = [ConceptNode(factor_name)]

    for variable in variables:
        list.append(variable)

    list_link = atomspace.add_link(types.ListLink, list)
    factor_arguments_predicate = EvaluationLink(
        PredicateNode("factor-arguments-list"),
        list_link
    )
    # print("factor arguments: ", factor_arguments_predicate)
    return factor_arguments_predicate


# dict keys for init_factor_graph:
KEY_FACTOR_EDGES = "factor_edges"
KEY_FACTOR_ARGUMENTS = "factor_arguments"


def init_factor_graph(dict):
    evaluation_links = atomspace.get_atoms_by_type(types.EvaluationLink)
    factors = set()
    factor_edges = []
    factor_arguments = []
    for link in evaluation_links:
        if not is_predicate(link, "probability"):
            continue
        variables = get_probability_variables(link)
        names = list(map(lambda node: node.name, variables))
        names.sort()
        factor_name = 'factor-' + '-'.join(names)
        if not factor_name in factors:
            factor_edges.extend(factor_graph_edge(factor_name, variables))
            factor_arguments.append(factor_arguments_list(factor_name, variables))
            factors.add(factor_name)

    # One probability rule has several factor edges: factor->variable
    factor_edges = list(set(factor_edges))
    dict[KEY_FACTOR_EDGES] = factor_edges
    dict[KEY_FACTOR_ARGUMENTS] = factor_arguments


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

    return values_link.out


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
    # print("factor graph: ", factor_graph_edges)
    print("factor arguments: ", factor_arguments)

    for edge in factor_graph_edges:
        list_link = edge.out[1]
        factor = list_link.out[0]
        variable = list_link.out[1]
        send_message_from_variable_to_factor(factor_graph_edges, variable, factor)
        send_message_from_factor_to_variable(factor_graph_edges, factor, variable)


run_belief_propagation_algorithm()
