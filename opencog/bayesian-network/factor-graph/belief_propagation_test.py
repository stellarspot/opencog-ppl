import unittest

from opencog.type_constructors import *
from opencog.utilities import initialize_opencog, finalize_opencog
from opencog.atomspace import PtrValue
from opencog.bindlink import evaluate_atom, execute_atom

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

    def test_belief_propagation(self):
        PROBABILITY_KEY = PredicateNode("probability")

        rain = ConceptNode('Rain')
        wet_grass = ConceptNode('WetGrass')
        wet_grass_given_rain = ImplicationLink(rain, wet_grass)

        rain.set_value(PROBABILITY_KEY, PtrValue(np.array([0.2, 0.8])))
        wet_grass_given_rain.set_value(PROBABILITY_KEY, PtrValue(np.array([[0.9, 0.1], [0.25, 0.75]])))

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


if __name__ == '__main__':
    unittest.main()
