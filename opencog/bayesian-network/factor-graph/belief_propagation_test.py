import unittest

from opencog.type_constructors import *
from opencog.utilities import initialize_opencog, finalize_opencog

from belief_propagation import *

import numpy as np


class BeliefPropagationTest(unittest.TestCase):

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

    def check_domain_value(self, atom, domain):
        domain_value = atom.get_value(PredicateNode("domain"))
        self.assertIsNotNone(domain_value)
        self.assertEqual(domain, domain_value.value())

    def check_tensor_value(self, atom, tensor):
        tensor_value = atom.get_value(PredicateNode("tensor"))
        self.assertIsNotNone(tensor)
        self.assertTrue(np.allclose(tensor, tensor_value.value()))

    def check_message_value(self, a, b, message_array):
        message = get_message_predicate(ConceptNode(a), ConceptNode(b))
        message_value = message.get_value(key_message())
        assert message_value, "Message value is not set!"
        self.assertTrue(np.allclose(message_array, message_value.value()))
