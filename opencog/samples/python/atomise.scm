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

def probability_end(x1, x2):
  prob_end = float(x1.name) * float(x2.name)
  return NumberNode(str(prob_end))

def probability_or(x1, x2):
   p1 = float(x1.name)
   p2 = float(x2.name)
   return NumberNode(str(p1 + p2 - p1 * p2))

counter = 0

def get_counter():
   global counter
   counter = counter + 1
   return NumberNode(str(counter))

")

(python-call-with-as "set_atomspace" (cog-atomspace))

(display
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: probability_end")
   (ListLink
    (Number "0.5")
    (Number "0.5")))))

(display
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: probability_or")
   (ListLink
    (Number "0.5")
    (Number "0.5")))))

(display
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: get_counter")
   (ListLink))))