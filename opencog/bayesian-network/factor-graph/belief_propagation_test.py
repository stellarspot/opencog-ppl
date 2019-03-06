import unittest

from opencog.type_constructors import *
from opencog.utilities import initialize_opencog, finalize_opencog
from opencog.atomspace import create_child_atomspace

from belief_propagation import *

import numpy as np


class BeliefPropagationTest(unittest.TestCase):

    def setUp(self):
        self.atomspace = AtomSpace()
        initialize_opencog(self.atomspace)

    def tearDown(self):
        finalize_opencog()
        del self.atomspace

    def create_child_atomspace(self):
        self.child_atomspace = create_child_atomspace(self.atomspace)
        initialize_opencog(self.child_atomspace)
        return self.child_atomspace

    def delete_child_atomspace(self):
        self.child_atomspace.clear()
        finalize_opencog()
        initialize_opencog(self.atomspace)

    def check_set_contains(self, set_link, atom):
        for a in set_link.get_out():
            if atom == a:
                return
        self.fail("result: " + str(set_link) + " does not contain: " + str(atom))

    def check_domain_value(self, atom, domain):
        domain_value = atom.get_value(PredicateNode("domain"))
        self.assertIsNotNone(domain_value)
        self.assertEqual(domain, domain_value.value())

    def check_tensor_value(self, atom, tensor):
        tensor_value = atom.get_value(PredicateNode("tensor"))
        self.assertIsNotNone(tensor_value)
        close = np.allclose(tensor, tensor_value.value())
        if not close:
            print('expected tensor:')
            print(tensor)
            print('result   tensor:')
            print(tensor_value.value())

        self.assertTrue(close)

    def check_tensors_equal(self, tensor1, tensor2):
        close = np.allclose(tensor1, tensor2)
        if not close:
            print('expected tensor:')
            print(tensor1)
            print('result   tensor:')
            print(tensor2)

        self.assertTrue(close)

    def check_message_value(self, a, b, message_array):
        message = get_message_predicate(ConceptNode(a), ConceptNode(b))
        message_value = message.get_value(key_message())
        assert message_value, "Message value is not set!"
        close = np.allclose(message_array, message_value.value())
        if not close:
            print("expected message:", message_array)
            print("result   message:", message_value.value())
        self.assertTrue(close)

    def check_variable_probability(self, probability, domain_size, tensor, evidence_index=None):

        # self.assertEqual(domain, probability.get_domain())
        # self.assertEqual(evidence, probability.evidence)
        self.assertEqual(domain_size, probability.domain_size)
        self.assertEqual(evidence_index, probability.evidence_index)
        self.check_tensors_equal(np.array(tensor), probability.get_probability_tensor())

    def check_declarative_variable_probability(self, probability, domain, tensor):

        self.assertEqual(domain, probability.domain)
        self.check_tensors_equal(np.array(tensor), probability.get_probability_tensor())
