# Sample from:
# https://github.com/noskill/opencog-intro

import os.path
from opencog.scheme_wrapper import scheme_eval, scheme_eval_h
from opencog.atomspace import TruthValue
from opencog.backwardchainer import BackwardChainer
from opencog.type_constructors import *
from opencog.utilities import initialize_opencog

from opencog.logger import Logger, log

# Logging will be written to opencog.log in the current directory.
# log.set_level('FINE')
# log.set_level('DEBUG')
log.set_level('INFO')
log.info("Starting the Socrates sample")

atomspace = AtomSpace()
initialize_opencog(atomspace)

scheme_eval(atomspace, '(use-modules (opencog))')
scheme_eval(atomspace, '(use-modules (opencog exec))')
scheme_eval(atomspace, '(use-modules (opencog query))')
scheme_eval(atomspace, '(use-modules (opencog rule-engine))')

pln_path = os.path.expanduser("/home/opencog/share/opencog/opencog/pln")
pln_config_path = os.path.expanduser("/home/opencog/share/opencog/opencog/pln/pln-config.scm")

scheme_eval(atomspace, '(add-to-load-path "{0}")'.format(pln_path))

scheme_eval(atomspace, '(load-from-path "{0}")'.format(pln_config_path))

InheritanceLink(ConceptNode("Socrates"), ConceptNode("man")).tv = TruthValue(0.8, 0.97)
InheritanceLink(ConceptNode("man"), ConceptNode("mortal")).tv = TruthValue(0.98, 0.94)

pattern = InheritanceLink(ConceptNode("Socrates"), ConceptNode("mortal"))

rule_base = ConceptNode("PLN")

chainer = BackwardChainer(atomspace, rule_base, pattern)

chainer.do_chain()
print(chainer.get_results())

InheritanceLink(ConceptNode("Socrates"), ConceptNode("man")).tv = TruthValue(0.7, 0.97)

pattern.tv = TruthValue(1.0, 0.0)
chainer = BackwardChainer(atomspace, rule_base, pattern)

chainer.do_chain()
print(chainer.get_results())
