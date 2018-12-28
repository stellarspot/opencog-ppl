from opencog.type_constructors import *
from belief_propagation import *
from test_lib import *

# P(Rain=true)=0.2
# P(Rain=false)=0.8

InheritanceLink(ConceptNode("TrueFalseValue"), ConceptNode("true"))
InheritanceLink(ConceptNode("TrueFalseValue"), ConceptNode("false"))

InheritanceLink(ConceptNode("Rain"), ConceptNode("TrueFalseValue"))
InheritanceLink(ConceptNode("WatsonGrass"), ConceptNode("Grass"))

probability_link([("Rain", "true")], 0.2)
probability_link([("Rain", "false")], 0.8)

run_belief_propagation_algorithm()


variable = ConceptNode("Rain")
factor = ConceptNode("Factor-Rain")
edge = factor_graph_edge(factor, variable)

# Test edge messages
message = get_value_list(edge, KEY_MESSAGE_VARIABLE_FACTOR)
assert message == [1.0, 1.0], "Incorrect message from variable to factor"

message = get_value_list(edge, KEY_MESSAGE_FACTOR_VARIABLE)
assert almost_equal_lists(message, [0.8, 0.2]), "Incorrect message from factor to variable"

# Test factor tensor
tensor = get_value_list(factor, KEY_FACTOR_TENSOR_VALUES)
assert almost_equal_lists(tensor, [0.8, 0.2]), "Incorrect message from factor to variable"
