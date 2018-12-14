from opencog.atomspace import AtomSpace, types

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *

atomspace = AtomSpace()
initialize_opencog(atomspace)


# Bayesian network graph

def probability_link(type, value, probability):
    return EvaluationLink(
        PredicateNode("probability"),
        AssociativeLink(ConceptNode(type), ConceptNode(value))
    )


def factor_graph_edge(factor_name, variables):
    list_link = atomspace.add_link(types.ListLink, [ConceptNode(factor_name), variables])
    return EvaluationLink(
        PredicateNode("graph-edge"),
        list_link
    )


probability_link("rain", "true", "0.2")
probability_link("rain", "false", "0.8")
probability_link("sprinkler", "on", "0.1")

EvaluationLink(
    PredicateNode("not-real-probability"),
    AssociativeLink(ConceptNode("test-not-include"), ConceptNode("value"))
)


def is_predicate(evalutation_link, predicate_name):
    return evalutation_link.out[0].name == predicate_name


# probability_link: predicate 'probability'
def get_probability_variables(probability_link):
    associative_link_type = 90
    out_set = probability_link.out
    variables = []
    for atom in out_set:
        # get variable from AssociativeLink
        if atom.type == associative_link_type:
            variables.append(atom.out[0])
    return variables


def generate_factor_graph():
    evaluationLinks = atomspace.get_atoms_by_type(types.EvaluationLink)
    factors = {}
    for link in evaluationLinks:
        if not is_predicate(link, "probability"):
            continue
        variables = get_probability_variables(link)
        factor_name = 'factor'
        for variable in variables:
            factor_name = factor_name + '-' + variable.name
        if not factor_name in factors:
            edge_link = factor_graph_edge(factor_name, variables)
            print('add factor graph edge', edge_link)
            factors[factor_name] = edge_link
    return TruthValue(1, 1)


factor_graph = generate_factor_graph()

print("factor graph: ", factor_graph)
