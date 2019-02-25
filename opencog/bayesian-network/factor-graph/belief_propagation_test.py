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

    def test_traffic_light(self):

        print('Test: Traffic Light and Risk')
        traffic_light = ConceptNode('TrafficLight')
        risk = ConceptNode('Risk')
        risk_given_traffic_light = ImplicationLink(traffic_light, risk)

        # [Green, Yellow, Red]
        traffic_light_probability = np.array([0.4, 0.25, 0.35])
        traffic_light_risk_joint_probability = np.array([[0.1, 0.9], [0.55, 0.45], [0.95, 0.05]])

        traffic_light.set_value(key_probability(), PtrValue(traffic_light_probability))
        risk_given_traffic_light.set_value(key_probability(), PtrValue(traffic_light_risk_joint_probability))

        belief_propagation(self.atomspace)

        # Check initial messages
        self.check_message_value("Variable-Risk", "Factor-Risk-TrafficLight", np.array([1, 1]))
        self.check_message_value("Factor-TrafficLight", "Variable-TrafficLight", traffic_light_probability)

        # Step 1
        self.check_message_value("Factor-Risk-TrafficLight", "Variable-TrafficLight", np.array([1, 1, 1]))
        self.check_message_value("Variable-TrafficLight", "Factor-Risk-TrafficLight", traffic_light_probability)

        # Step 2
        self.check_message_value("Variable-TrafficLight", "Factor-TrafficLight", np.array([1, 1, 1]))
        msg = np.tensordot(traffic_light_risk_joint_probability, traffic_light_probability, axes=(0, 0))
        self.check_message_value("Factor-Risk-TrafficLight", "Variable-Risk", msg)

    def test_traffic_light_given_risk(self):

        print('Test: Traffic Light and Risk given Risk')
        traffic_light = ConceptNode('TrafficLight')
        risk = ConceptNode('Risk')
        risk_given_traffic_light = ImplicationLink(traffic_light, risk)

        # [Green, Yellow, Red]
        traffic_light_probability = np.array([0.4, 0.25, 0.35])
        traffic_light_risk_joint_probability = np.array([[0.1, 0.9], [0.55, 0.45], [0.95, 0.05]])

        traffic_light.set_value(key_probability(), PtrValue(traffic_light_probability))
        risk_given_traffic_light.set_value(key_probability(), PtrValue(traffic_light_risk_joint_probability))

        # P(TL=Yellow|R=High)
        # 1) P(TL=Yellow, R=High)
        # TL=Yellow, index=1
        # R=High, index=0
        traffic_light.set_value(key_evidence(), PtrValue(1))
        risk_given_traffic_light.set_value(key_evidence(), PtrValue(0))

        belief_propagation(self.atomspace)


if __name__ == '__main__':
    unittest.main()
