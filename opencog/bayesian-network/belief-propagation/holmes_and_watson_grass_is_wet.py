from opencog.type_constructors import *

from belief_propagation import probability_link
from belief_propagation import run_belief_propagation_algorithm

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

run_belief_propagation_algorithm()
