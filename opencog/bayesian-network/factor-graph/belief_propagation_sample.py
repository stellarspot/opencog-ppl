from opencog.type_constructors import *
from opencog.utilities import initialize_opencog, finalize_opencog
from opencog.atomspace import PtrValue
from opencog.atomspace import create_child_atomspace as create_temp_atomspace
from belief_propagation import *

# Initialize AtomSpace
atomspace = AtomSpace()
initialize_opencog(atomspace)


def create_child_atomspace():
    global child_atomspace
    child_atomspace = create_temp_atomspace(atomspace)
    initialize_opencog(child_atomspace)
    return child_atomspace


def delete_child_atomspace():
    global child_atomspace
    child_atomspace.clear()
    finalize_opencog()
    initialize_opencog(atomspace)


# Define Atoms and Links
rain = ConceptNode('Rain')
sprinkler = ConceptNode('Sprinkler')
holmes_grass = ConceptNode('HolmesGrass')
watson_grass = ConceptNode('WatsonGrass')
watson_grass_given_rain = ImplicationLink(rain, watson_grass)
holmes_grass_given_sprinkler_rain = ImplicationLink(ListLink(sprinkler, rain), holmes_grass)

# Define probabilities values
# Rain a priory probability
rain.set_value(key_domain(), PtrValue(["true", "false"]))
rain.set_value(key_probability(), PtrValue({"true": 0.2}))

# Sprinkler a priory probability
sprinkler.set_value(key_domain(), PtrValue(["switch-on", "switch-off"]))
sprinkler.set_value(key_probability(), PtrValue({"switch-on": 0.1}))

# Watson Grass given Rain conditional probability table
watson_grass_given_rain_probability = [[1.0, 0.0],
                                       [0.2, 0.8]]
watson_grass_given_rain.set_value(key_probability(), PtrValue(watson_grass_given_rain_probability))

# Holmes Grass given Sprinkler and Rain conditional probability table
holmes_grass_given_sprinkler_rain_probability = [[[1.0, 0.0],
                                                  [0.9, 0.1]],
                                                 [[1.0, 0.0],
                                                  [0.0, 1.0]]]
holmes_grass_given_sprinkler_rain.set_value(key_probability(),
                                            PtrValue(holmes_grass_given_sprinkler_rain_probability))

# P(HG=wet)
# P(HG=wet, WG, S, R)
# HG=wet, index=0
child_atomspace = create_child_atomspace()
holmes_grass.set_value(key_evidence(), PtrValue(0))
marginalization_divisor = belief_propagation(child_atomspace)

dump_atomspace(child_atomspace)

delete_child_atomspace()

# P(HG=wet, R=true)
# P(HG=wet, WG, S, R=true)
# HG=wet, index=0
# R=true, index=0

child_atomspace = create_child_atomspace()
holmes_grass.set_value(key_evidence(), PtrValue(0))
rain.set_value(key_evidence(), PtrValue(0))
marginalization_dividend = belief_propagation(child_atomspace)

delete_child_atomspace()

probability_rain_given_holmes_grass = marginalization_dividend / marginalization_divisor

print()
print('probability rain given Holmes wet grass:', probability_rain_given_holmes_grass)
