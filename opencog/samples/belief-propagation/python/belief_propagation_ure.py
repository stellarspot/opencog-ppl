from opencog.utilities import initialize_opencog
from opencog.type_constructors import *
from opencog.bindlink import bindlink
from opencog.bindlink import execute_atom

# AtomSpace Initialization
atomspace = AtomSpace()
initialize_opencog(atomspace)

CDV_KEY = PredicateNode('CDV')
SHAPE_KEY = PredicateNode('shape')
TENSOR_KEY = PredicateNode('tensor')

FACTOR_KEY = PredicateNode('factor')
VARIABLE_KEY = PredicateNode('variable')
EDGE_KEY = PredicateNode('edge')


# Utility methods

def show_atomspace():
    print('--- AtomSpace Dump---')
    for atom in atomspace:
        print(atom)
    print('---------------------')


# Belief Propagation Utility methods

def bool_to_tv(b):
    if not b:
        return TruthValue(0, 1)
    return TruthValue(1, 1)


def float_value_to_list(value):
    list = None
    if value:
        list = value.to_list()
    return list


def eval_has_value(atom, key):
    value = atom.get_value(key)
    if not value:
        return TruthValue(0, 1)
    return TruthValue(1, 1)


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
    show_value('tensor', atom, TENSOR_KEY)
    print()


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
        variable
    )


def get_factor_predicate(factor):
    return EvaluationLink(
        FACTOR_KEY,
        factor
    )


def get_edge_predicate(factor, var):
    return EvaluationLink(
        EDGE_KEY,
        ListLink(
            factor,
            var
        )
    )


def set_variable_shape(v, variable):
    shape = v.get_value(SHAPE_KEY)
    variable.set_value(SHAPE_KEY, shape)


def set_factor_tensor(atom, factor):
    shape = atom.get_value(SHAPE_KEY)
    factor.set_value(SHAPE_KEY, shape)
    tensor = atom.get_value(CDV_KEY)
    factor.set_value(TENSOR_KEY, tensor)


# ; =====================================================================
# ; ConceptNode to Variable rule
# ;
# ; A
# ; |-
# ; Evaluation
# ;    Predicate "factor-node"
# ;    Concept "Factor-A"
# ;
# ; Evaluation
# ;    Predicate "variable-node"
# ;    Concept "Variable-A"
# ;
# ; Evaluation
# ;    Predicate "graph-edge"
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
    # bindlink(atomspace, bind_link)
    res = bindlink(atomspace, bind_link)
    print(res)


def init_factor_graph_concept_node_formula(v):
    print('init_factor_graph_concept_node_formula', v)

    variable = get_variable_node(v)
    factor = get_factor_node([v])

    # generate factor graph predicates
    variable_predicate = get_variable_predicate(variable)
    factor_predicate = get_factor_predicate(factor)
    edge = get_edge_predicate(factor, variable)

    # set variable shape
    set_variable_shape(v, variable)

    # set factor tensor
    set_factor_tensor(v, factor)

    return ListLink(
        variable_predicate,
        factor_predicate,
        edge
    )


def init_factor_graph():
    init_factor_graph_concept_node()
