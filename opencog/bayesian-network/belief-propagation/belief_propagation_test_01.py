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

# message: variable to factor
message = get_variable_factor_message(variable, factor)
assert message == [1.0, 1.0], "Incorrect message from variable to factor"

# message: factor to variable
message = get_factor_variable_message(factor, variable)
assert almost_equal_lists(message, [0.8, 0.2]), "Incorrect message from factor to variable"

# factor tensor
tensor = get_value_list(factor, KEY_FACTOR_TENSOR_VALUES)
assert almost_equal_lists(tensor, [0.8, 0.2]), "Incorrect message from factor to variable"
