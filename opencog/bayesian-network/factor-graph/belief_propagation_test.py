import unittest

from opencog.type_constructors import *
from opencog.utilities import initialize_opencog, finalize_opencog
from opencog.atomspace import PtrValue
from opencog.bindlink import execute_atom

from belief_propagation import *

import numpy as np


class PtrValueTest(unittest.TestCase):

    def setUp(self):
        self.atomspace = AtomSpace()
        initialize_opencog(self.atomspace)

    def tearDown(self):
        finalize_opencog()
        del self.atomspace

    def check_set_contains(self, set_link, atom):
        for a in set_link.get_out():
            if atom == a:
                return
        self.fail("result: " + str(set_link) + " does not contain: " + str(atom))

    def check_tensor_value(self, atom, tensor):
        tensor_value = atom.get_value(PredicateNode("tensor"))
        self.assertIsNotNone(tensor)
        self.assertTrue(np.allclose(tensor, tensor_value.value()))

    def check_domain_value(self, atom, domain):
        domain_value = atom.get_value(PredicateNode("domain"))
        self.assertIsNotNone(domain_value)
        self.assertEqual(domain, domain_value.value())

    def test_belief_propagation(self):

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


if __name__ == '__main__':
    unittest.main()
