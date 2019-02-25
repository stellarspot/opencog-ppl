import unittest

from opencog.type_constructors import *
from opencog.utilities import initialize_opencog, finalize_opencog
from opencog.atomspace import PtrValue
from opencog.bindlink import execute_atom

from belief_propagation import *
from belief_propagation_test import BeliefPropagationTest

import numpy as np


class BeliefPropagationTrafficLightRiskTest(BeliefPropagationTest):

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
