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

rain_probability = np.array([0.2, 0.8])
rain_wet_grass_joint_probability = np.array([[0.9, 0.1], [0.25, 0.75]])

rain.set_value(key_probability(), PtrValue(rain_probability))
wet_grass_given_rain.set_value(key_probability(), PtrValue(rain_wet_grass_joint_probability))

print('Rain = T', rain_wet_grass_joint_probability[0])
print('Rain = F', rain_wet_grass_joint_probability[1])

print()
tensor = np.array([[1, 2, 3], [4, 5, 6]])
print(tensor)
res = np.tensordot(tensor, np.array([1, 1]), axes=(0, 0))
print(res)
res = np.tensordot(tensor, np.array([1, 1, 1]), axes=(1, 0))
print(res)
print()

# print(rain.get_value(key_probability()).value())
# print(wet_grass_given_rain.get_value(key_probability()).value())

belief_propagation(atomspace)
