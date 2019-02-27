import unittest

from opencog.type_constructors import *
from opencog.atomspace import PtrValue
from opencog.bindlink import execute_atom

from belief_propagation import *
from belief_propagation_test import BeliefPropagationTest

import numpy as np


class BeliefPropagationRainWetGrassTest(BeliefPropagationTest):

    def init_rain_wet_grass_bayesian_network(self):
        print('Test: Sherlock Holmes and  Wet Grass')
        rain = ConceptNode('Rain')
        sprinkler = ConceptNode('Sprinkler')
        holmes_grass = ConceptNode('HolmesGrass')
        watson_grass = ConceptNode('WatsonGrass')
        watson_grass_given_rain = ImplicationLink(rain, watson_grass)
        holmes_grass_given_rain_sprinkler = ImplicationLink(ListLink(rain, sprinkler), watson_grass)

        self.rain_probability = np.array([0.2, 0.8])
        rain.set_value(key_probability(), PtrValue(self.rain_probability))

        self.sprinkler_probability = np.array([0.1, 0.9])
        sprinkler.set_value(key_probability(), PtrValue(self.sprinkler_probability))

        self.watson_grass_given_rain_probability = np.array([[1.0, 0.0], [0.2, 0.8]])
        watson_grass_given_rain.set_value(key_probability(), PtrValue(self.watson_grass_given_rain_probability))

        self.holmes_grass_given_rain_sprinkler_probability = np.array([[1.0, 0.0], [0.2, 0.8]])
        holmes_grass_given_rain_sprinkler.set_value(key_probability(),
                                                    PtrValue(self.holmes_grass_given_rain_sprinkler_probability))

    def test_rain_wet_grass(self):
        self.init_rain_wet_grass_bayesian_network()

        child_atomspace = self.create_child_atomspace()
        marginalization = belief_propagation(child_atomspace)

        # check domain
        self.check_domain_value(ConceptNode("Variable-Rain"), 2)
        self.check_domain_value(ConceptNode("Variable-Sprinkler"), 2)
        self.check_domain_value(ConceptNode("Variable-WatsonGrass"), 2)

        # check probability tensors

        self.check_tensor_value(ConceptNode("Factor-Rain"), self.rain_probability)
        self.check_tensor_value(ConceptNode("Factor-Sprinkler"), self.sprinkler_probability)

        # check messages

        self.initial_message = np.array([1, 1])

        self.check_message_value("Variable-WatsonGrass", "Factor-Rain-WatsonGrass", self.initial_message)
        self.check_message_value("Factor-Rain", "Variable-Rain", self.rain_probability)

        self.delete_child_atomspace()

        print('marginalization', marginalization)


if __name__ == '__main__':
    unittest.main()
