from opencog.type_constructors import *
from opencog.atomspace import TruthValue

# =============================================================================
# Crisp logic entailment (Deduction) Rule.
#
#  A->B
#  B->C
#  |-
#  A->C
#
# See https://github.com/opencog/atomspace/tree/master/examples/rule-engine for more details.
# -----------------------------------------------------------------------------

deduction_rule = BindLink(
    VariableList(
        TypedVariableLink(
            VariableNode('$A'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$B'),
            TypeNode('ConceptNode')),
        TypedVariableLink(
            VariableNode('$C'),
            TypeNode('ConceptNode'))),
    AndLink(
        InheritanceLink(
            VariableNode('$A'),
            VariableNode('$B')),
        InheritanceLink(
            VariableNode('$B'),
            VariableNode('$C')),
        NotLink(
            EqualLink(
                VariableNode('$A'),
                VariableNode('$C')))),
    ExecutionOutputLink(
        GroundedSchemaNode('py: deduction_formula'),
        ListLink(
            InheritanceLink(
                VariableNode('$A'),
                VariableNode('$C')),
            InheritanceLink(
                VariableNode('$A'),
                VariableNode('$B')),
            InheritanceLink(
                VariableNode('$B'),
                VariableNode('$C')))))


# -----------------------------------------------------------------------------
# Deduction Formula
#
# If both confidence and strength of A->B and B->C are above 0.5 then
# set the TV of A->C to (stv 1 1)
# -----------------------------------------------------------------------------

def deduction_formula(AC, AB, BC):
    tv1 = AB.tv
    tv2 = BC.tv

    if tv1.mean > 0.5 and tv2.mean > 0.5 and tv1.confidence > 0.5 and tv2.confidence > 0.5:
        AC.tv = TruthValue(1, 1)
    else:
        AC.tv = TruthValue(0, 0)

    return AC


#############################
## Associate rules to PLN  ##
#############################

deduction_rule_name = DefinedSchemaNode("deduction-rule")

DefineLink(
    deduction_rule_name,
    deduction_rule)

deduction_rbs = ConceptNode("deduction-rule-base")

InheritanceLink(
    deduction_rbs,
    ConceptNode("URE"))

MemberLink(
    deduction_rule_name,
    deduction_rbs
)

# Set URE maximum-iterations
from opencog.scheme_wrapper import scheme_eval

execute_code = \
    '''
    (use-modules (opencog rule-engine))
    (ure-set-num-parameter (ConceptNode "deduction-rule-base") "URE:maximum-iterations" 30)
    '''

scheme_eval(atomspace, execute_code)
