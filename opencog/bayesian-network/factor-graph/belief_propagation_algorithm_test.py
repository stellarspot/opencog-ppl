import unittest

from opencog.type_constructors import *
from opencog.atomspace import PtrValue
from opencog.bindlink import execute_atom

from belief_propagation import *
from belief_propagation_test import BeliefPropagationTest

import numpy as np


class BeliefPropagationAlgorithmTest(BeliefPropagationTest):

    def test_init_factor_graph_implication_link_rule(self):
        a = ConceptNode("A")
        b = ConceptNode("B")

        implication = ImplicationLink(a, b)
        implication_probability = np.array([[0.9, 0.1], [0.8, 0.2]])
        implication.set_value(key_probability(), PtrValue(implication_probability))

        child_atomspace = self.create_child_atomspace()
        execute_atom(child_atomspace, init_factor_graph_implication_link_rule())

        # check domain
        self.check_domain_value(ConceptNode("Variable-A"), 2)
        self.check_domain_value(ConceptNode("Variable-B"), 2)

        # check probability tensor
        self.check_tensor_value(ConceptNode("Factor-A-B"), implication_probability)

        self.delete_child_atomspace()

    def test_init_factor_graph_implication_link_product_rule2(self):
        a = ConceptNode("A")
        b = ConceptNode("B")
        c = ConceptNode("C")

        implication = ImplicationLink(ListLink(a, b), c)
        implication_probability = np.array([[[0.9, 0.1], [0.8, 0.2]], [[0.7, 0.3], [0.6, 0.4]]])
        implication.set_value(key_probability(), PtrValue(implication_probability))

        child_atomspace = self.create_child_atomspace()
        execute_atom(child_atomspace, init_factor_graph_implication_link_product_rule())

        # check domain
        self.check_domain_value(ConceptNode("Variable-A"), 2)
        self.check_domain_value(ConceptNode("Variable-B"), 2)
        self.check_domain_value(ConceptNode("Variable-C"), 2)

        # check probability tensors
        self.check_tensor_value(ConceptNode("Factor-A-B-C"), implication_probability)

        self.delete_child_atomspace()

    # @unittest.skip
    def test_init_factor_graph_implication_link_product_rule3(self):
        a = ConceptNode("A")
        b = ConceptNode("B")
        c = ConceptNode("C")
        d = ConceptNode("D")

        implication = ImplicationLink(ListLink(a, b, c), d)
        implication_probability = np.array(
            [[[[0.9, 0.1], [0.8, 0.2]],
              [[0.7, 0.3], [0.6, 0.4]]],
             [[[0.9, 0.1], [0.8, 0.2]],
              [[0.7, 0.3], [0.6, 0.4]]]])

        implication.set_value(key_probability(), PtrValue(implication_probability))

        child_atomspace = self.create_child_atomspace()
        execute_atom(child_atomspace, init_factor_graph_implication_link_product_rule())

        # check domain
        self.check_domain_value(ConceptNode("Variable-A"), 2)
        self.check_domain_value(ConceptNode("Variable-B"), 2)
        self.check_domain_value(ConceptNode("Variable-C"), 2)
        self.check_domain_value(ConceptNode("Variable-D"), 2)

        # check probability tensors
        self.check_tensor_value(ConceptNode("Factor-A-B-C-D"), implication_probability)

        self.delete_child_atomspace()


if __name__ == '__main__':
    unittest.main()
