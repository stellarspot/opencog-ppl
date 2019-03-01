import unittest

from opencog.type_constructors import *
from opencog.atomspace import PtrValue

from belief_propagation import *
from belief_propagation_test import BeliefPropagationTest

import numpy as np


class BeliefPropagationRainWetGrassTest(BeliefPropagationTest):

    def init_rain_wet_grass_bayesian_network(self):
        print('Test: Sherlock Holmes and  Wet Grass')
        self.rain = ConceptNode('Rain')
        self.sprinkler = ConceptNode('Sprinkler')
        self.holmes_grass = ConceptNode('HolmesGrass')
        self.watson_grass = ConceptNode('WatsonGrass')
        self.watson_grass_given_rain = ImplicationLink(self.rain, self.watson_grass)
        self.holmes_grass_given_rain_sprinkler = ImplicationLink(ListLink(self.rain, self.sprinkler), self.holmes_grass)

        self.rain_probability = np.array([0.2, 0.8])
        self.rain.set_value(key_probability(), PtrValue(self.rain_probability))

        self.sprinkler_probability = np.array([0.1, 0.9])
        self.sprinkler.set_value(key_probability(), PtrValue(self.sprinkler_probability))

        self.watson_grass_given_rain_probability = np.array(
            [[1.0, 0.0],
             [0.2, 0.8]])
        self.watson_grass_given_rain.set_value(key_probability(), PtrValue(self.watson_grass_given_rain_probability))

        self.holmes_grass_given_rain_sprinkler_probability = np.array(
            [[[1.0, 0.0],
              [0.1, 0.9]],
             [[1.0, 0.0],
              [0.0, 1.0]]])
        self.holmes_grass_given_rain_sprinkler.set_value(key_probability(),
                                                    PtrValue(self.holmes_grass_given_rain_sprinkler_probability))

    def test_rain_wet_grass(self):
        self.init_rain_wet_grass_bayesian_network()

        child_atomspace = self.create_child_atomspace()
        marginalization = belief_propagation(child_atomspace)

        # check domain
        self.check_domain_value(ConceptNode("Variable-Rain"), 2)
        self.check_domain_value(ConceptNode("Variable-Sprinkler"), 2)
        self.check_domain_value(ConceptNode("Variable-WatsonGrass"), 2)
        self.check_domain_value(ConceptNode("Variable-HolmesGrassGrass"), 2)

        # check probability tensors

        self.check_tensor_value(ConceptNode("Factor-Rain"), self.rain_probability)
        self.check_tensor_value(ConceptNode("Factor-Sprinkler"), self.sprinkler_probability)

        # check messages

        self.initial_message = np.array([1, 1])

        self.check_message_value("Variable-WatsonGrass", "Factor-Rain-WatsonGrass", self.initial_message)
        self.check_message_value("Factor-Rain", "Variable-Rain", self.rain_probability)

        self.delete_child_atomspace()

        print('marginalization', marginalization)

    def test_rain_wet_grass(self):
        self.init_rain_wet_grass_bayesian_network()


        # P(HG=wet)
        # P(HG=wet, WG, S, R)
        # HG=wet, index=0

        child_atomspace = self.create_child_atomspace()
        self.holmes_grass.set_value(key_evidence(), PtrValue(0))
        marginalization_divisor = belief_propagation(child_atomspace)

        print('marginalization divisor:', marginalization_divisor)

        # check domain
        self.check_domain_value(ConceptNode("Variable-Rain"), 2)
        self.check_domain_value(ConceptNode("Variable-Sprinkler"), 2)
        self.check_domain_value(ConceptNode("Variable-WatsonGrass"), 2)
        self.check_domain_value(ConceptNode("Variable-HolmesGrass"), 1)

        self.delete_child_atomspace()

        # P(HG=wet, R=true)
        # P(HG=wet, WG, S, R=true)
        # HG=wet, index=0
        # R=true, index=0

        child_atomspace = self.create_child_atomspace()
        self.holmes_grass.set_value(key_evidence(), PtrValue(0))
        self.rain.set_value(key_evidence(), PtrValue(0))
        marginalization_divident = belief_propagation(child_atomspace)

        print('marginalization divident:', marginalization_divident)
        self.delete_child_atomspace()

        probability_rain_given_holmes_grass = marginalization_divident / marginalization_divisor

        print('probability rain given Holmes wet grass:', probability_rain_given_holmes_grass)


if __name__ == '__main__':
    unittest.main()
