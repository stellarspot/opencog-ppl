(use-modules (opencog) (opencog python) (opencog exec))
(use-modules (opencog logger))

(python-eval "
from opencog.atomspace import AtomSpace, types, TruthValue

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *


atomspace = ''
def set_atomspace(a):
      global atomspace
      atomspace = a
      initialize_opencog(a)
      return TruthValue(1, 1)

def and_link(x1, x2):
      print(\"return AndLink for: \\n\", x1, x2)
      return AndLink(x1, x2)

")

(python-call-with-as "set_atomspace" (cog-atomspace))

(display
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: and_link")
   (ListLink
    (ConceptNode "One")
    (ConceptNode "Two")))))

(newline)