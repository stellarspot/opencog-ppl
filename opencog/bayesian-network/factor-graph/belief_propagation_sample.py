from opencog.type_constructors import *
from opencog.utilities import initialize_opencog
from opencog.atomspace import PtrValue
from opencog.bindlink import execute_atom

import numpy as np

# Initialize AtomSpace
atomspace = AtomSpace()
initialize_opencog(atomspace)

from belief_propagation import *

rain = ConceptNode('Rain')
wet_grass = ConceptNode('WetGrass')
wet_grass_given_rain = ImplicationLink(rain, wet_grass)

rain.set_value(key_probability(), PtrValue(np.array([0.2, 0.8])))
wet_grass_given_rain.set_value(key_probability(), PtrValue(np.matrix([[0.9, 0.1], [0.25, 0.75]])))

print(rain.get_value(key_probability()).value())
print(wet_grass_given_rain.get_value(key_probability()).value())

belief_propagation(atomspace)
