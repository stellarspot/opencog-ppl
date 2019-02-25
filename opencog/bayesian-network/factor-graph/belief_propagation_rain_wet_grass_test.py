import unittest

from opencog.type_constructors import *
from opencog.utilities import initialize_opencog, finalize_opencog
from opencog.atomspace import PtrValue
from opencog.bindlink import execute_atom

from belief_propagation import *
from belief_propagation_test import BeliefPropagationTest

import numpy as np


class BeliefPropagationRainWetGrassTest(BeliefPropagationTest):

    def test_rain_wet_grass(self):
        print('Test: Rain and Wet Grass')
        rain = ConceptNode('Rain')
        wet_grass = ConceptNode('WetGrass')
        wet_grass_given_rain = ImplicationLink(rain, wet_grass)

        rain_probability = np.array([0.2, 0.8])
        rain_wet_grass_joint_probability = np.array([[0.9, 0.1], [0.25, 0.75]])

        rain.set_value(key_probability(), PtrValue(rain_probability))
        wet_grass_given_rain.set_value(key_probability(), PtrValue(rain_wet_grass_joint_probability))

        belief_propagation(self.atomspace)

        # Check Variables
        res = execute_atom(self.atomspace,
                           GetLink(
                               EvaluationLink(
                                   PredicateNode("variable"),
                                   VariableNode("$V"))))
        self.check_set_contains(res, ConceptNode("Variable-Rain"))

        # Check Factors
        res = execute_atom(self.atomspace,
                           GetLink(
                               EvaluationLink(
                                   PredicateNode("factor"),
                                   VariableNode("$F"))))
        self.check_set_contains(res, ConceptNode("Factor-Rain"))

        # Check Variable shapes
        self.check_domain_value(ConceptNode("Variable-Rain"), 2)
        self.check_domain_value(ConceptNode("Variable-WetGrass"), 2)

        # Check Factor tensors
        self.check_tensor_value(ConceptNode("Factor-Rain"), rain_probability)
        self.check_tensor_value(ConceptNode("Factor-Rain-WetGrass"), rain_wet_grass_joint_probability)

        # Check initial messages
        self.check_message_value("Variable-WetGrass", "Factor-Rain-WetGrass", np.array([1, 1]))
        self.check_message_value("Factor-Rain", "Variable-Rain", rain_probability)


if __name__ == '__main__':
    unittest.main()
