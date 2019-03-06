import unittest

from opencog.type_constructors import *
from opencog.atomspace import PtrValue

from belief_propagation import *
from belief_propagation_test import BeliefPropagationTest

import numpy as np


class BeliefPropagationTrafficLightRiskTest(BeliefPropagationTest):

    def init_traffic_light(self):
        self.traffic_light = ConceptNode('TrafficLight')
        self.risk = ConceptNode('Risk')
        self.risk_given_traffic_light = ImplicationLink(self.traffic_light, self.risk)

        # [Green, Yellow, Red]
        self.traffic_light_probability = [0.4, 0.25, 0.35]
        self.traffic_light_risk_joint_probability = [[0.1, 0.9], [0.55, 0.45], [0.95, 0.05]]

        self.traffic_light.set_value(key_probability(), PtrValue(Probability(self.traffic_light_probability)))
        self.risk_given_traffic_light.set_value(key_probability(),
                                                PtrValue(Probability(self.traffic_light_risk_joint_probability)))

    def test_traffic_light(self):
        print('Test: Traffic Light and Risk')

        self.init_traffic_light()

        child_atomspace = self.create_child_atomspace()
        belief_propagation(child_atomspace)

        # Check initial messages
        self.check_message_value("Variable-Risk", "Factor-TrafficLight-Risk", np.array([1, 1]))
        self.check_message_value("Factor-TrafficLight", "Variable-TrafficLight", self.traffic_light_probability)

        # Step 1
        self.check_message_value("Factor-TrafficLight-Risk", "Variable-TrafficLight", np.array([1, 1, 1]))
        self.check_message_value("Variable-TrafficLight", "Factor-TrafficLight-Risk", self.traffic_light_probability)

        # Step 2
        self.check_message_value("Variable-TrafficLight", "Factor-TrafficLight", np.array([1, 1, 1]))
        msg = np.tensordot(self.traffic_light_risk_joint_probability, self.traffic_light_probability, axes=(0, 0))
        self.check_message_value("Factor-TrafficLight-Risk", "Variable-Risk", msg)

        self.delete_child_atomspace()

    def test_traffic_light_given_risk(self):
        print('Test: Traffic Light and Risk given Risk')

        self.init_traffic_light()

        self.risk.set_value(key_evidence(), PtrValue(0))
        # self.risk.set_value(key_evidence(), Probability(evidence_index=0))
        child_atomspace = self.create_child_atomspace()
        marginalization_divisor = belief_propagation(child_atomspace)

        self.delete_child_atomspace()
        self.assertAlmostEqual(0.51, marginalization_divisor)

        # Marginalization dividend
        # P(TL=Yellow, R=High)
        # TL=Yellow, index=1
        # R=High, index=0

        self.traffic_light.set_value(key_evidence(), PtrValue(1))
        self.risk.set_value(key_evidence(), PtrValue(0))
        child_atomspace = self.create_child_atomspace()
        marginalization_dividend = belief_propagation(child_atomspace)

        self.delete_child_atomspace()
        self.assertAlmostEqual(0.1375, marginalization_dividend)

        probability_risk_given_traffic_light = marginalization_dividend / marginalization_divisor
        self.assertAlmostEqual(0.27, probability_risk_given_traffic_light, 2)


if __name__ == '__main__':
    unittest.main()
