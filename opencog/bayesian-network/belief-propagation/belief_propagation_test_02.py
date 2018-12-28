from opencog.type_constructors import *
from belief_propagation import *
from test_lib import *

# P(Rain=true)=0.2
# P(Rain=false)=0.8
# P(WatsonGrass=wet|Rain=true)=0.9
# P(WatsonGrass=dry|Rain=true)=0.1
# P(WatsonGrass=wet|Rain=false)=0.25
# P(WatsonGrass=dry|Rain=false)=0.75


InheritanceLink(ConceptNode("TrueFalseValue"), ConceptNode("true"))
InheritanceLink(ConceptNode("TrueFalseValue"), ConceptNode("false"))

InheritanceLink(ConceptNode("Grass"), ConceptNode("wet"))
InheritanceLink(ConceptNode("Grass"), ConceptNode("dry"))

InheritanceLink(ConceptNode("Rain"), ConceptNode("TrueFalseValue"))
InheritanceLink(ConceptNode("WatsonGrass"), ConceptNode("Grass"))

probability_link([("Rain", "true")], 0.2)
probability_link([("Rain", "false")], 0.8)

probability_link([("Rain", "true"), ("WatsonGrass", "wet")], 0.9)
probability_link([("Rain", "true"), ("WatsonGrass", "dry")], 0.1)
probability_link([("Rain", "false"), ("WatsonGrass", "wet")], 0.25)
probability_link([("Rain", "false"), ("WatsonGrass", "dry")], 0.75)

run_belief_propagation_algorithm()

var_rain = ConceptNode("Rain")
var_watson_grass = ConceptNode("WatsonGrass")
factor_p1 = ConceptNode("Factor-Rain-WatsonGrass")
factor_p2 = ConceptNode("Factor-Rain")

edge_p1_rain = factor_graph_edge(factor_p1, var_rain)
edge_p2_watson_grass = factor_graph_edge(factor_p1, var_watson_grass)

# P(WatsonGrass, Rain) = P(WatsonGrass|Rain) * P(Rain)
# P(WatsonGrass, Rain) = P1(WatsonGrass,Rain) * P2(Rain)
#
# Factor Graph
# WG - P2 - Rain - P1


# Tensors

# P2(Rain)
# Rain {false, true}
tensor_p2 = get_value_list(factor_p2, KEY_FACTOR_TENSOR_VALUES)
assert almost_equal_lists(tensor_p2, [0.8, 0.2])

# P1(Rain, WatsonGrass)
# Rain {false, true}
# WatsonGrass {dry, wet}
tensor_p1 = get_value_list(factor_p1, KEY_FACTOR_TENSOR_VALUES)
assert almost_equal_lists(tensor_p1, [0.75, 0.1, 0.25, 0.9])

# Step 1
# WG -> P1
message = get_variable_factor_message(var_watson_grass, factor_p1)
assert message == [1.0, 1.0]

# P1 -> Rain
message = get_factor_variable_message(factor_p2, var_rain)
assert almost_equal_lists(message, [0.8, 0.2])

# Step 2

# Rain-> P1
message = get_variable_factor_message(var_rain, factor_p1)
assert almost_equal_lists(message, [0.8, 0.2])

# P1
# tensor [0.75, 0.1, 0.25, 0.9] x [1, 1]

# P1 -> Rain
# income messages: [1.0, 1.0]
message = get_factor_variable_message(factor_p1, var_rain)
assert almost_equal_lists(message, [0.85, 1.15])

# P1 -> WatsonGrass
# income messages: [0.8, 0.2]
message = get_factor_variable_message(factor_p1, var_watson_grass)
assert almost_equal_lists(message, [0.65, 0.25])

# Rain-> P2
message = get_variable_factor_message(var_rain, factor_p2)
assert almost_equal_lists(message, [0.85, 1.15])
