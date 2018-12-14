(use-modules (opencog) (opencog query) (opencog exec))
(use-modules (opencog python))

; Bayesian Network
; Belief Propagation

; Domains
(InheritanceLink (Concept "true") (Concept "TrueFalseValue"))
(InheritanceLink (Concept "false") (Concept "TrueFalseValue"))

(InheritanceLink (Concept "switch-on") (Concept "Switch"))
(InheritanceLink (Concept "swithc-off") (Concept "Switch"))

(InheritanceLink (Concept "wet") (Concept "Grass"))
(InheritanceLink (Concept "dry") (Concept "Grass"))

(InheritanceLink (Concept "Rain") (Concept "TrueFalseValue"))
(InheritanceLink (Concept "Sprinkler") (Concept "Switch"))
(InheritanceLink (Concept "WatsonGrass") (Concept "Grass"))
(InheritanceLink (Concept "HolmesGrass") (Concept "Grass"))

; Sherlock Holmes and wet grass

; Rain
; P(R)
; true 0.2
; false 0.8

(EvaluationLink (stv 0.2 1)
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "true")))


(EvaluationLink (stv 0.8 1)
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "false")))


; Sprinkler
; P(S)
; switch-on  0.1
; switch-off 0.9

(EvaluationLink (stv 0.1 1)
 (PredicateNode "probability")
 (AssociativeLink (Concept "Sprinkler") (Concept "switch-on")))

(EvaluationLink (stv 0.9 1)
 (PredicateNode "probability")
 (AssociativeLink (Concept "Sprinkler") (Concept "switch-off")))

; Watson grass
; P(WG|R)
; R      wet  dry
; true   1.0  0.0
; false  0.2  0.8

(EvaluationLink (stv 1.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "true" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet"))))

(EvaluationLink (stv 0.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "true" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry"))))

(EvaluationLink (stv 0.2 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "false" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet"))))

(EvaluationLink (stv 0.8 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "false" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry"))))

; Holmes grass
; P(HG|R)
; S          R      wet  dry
; switch-on  true   1.0  0.0
; switch-on  false  0.9  0.1
; switch-off true   1      0
; switch-off false  0      1

(EvaluationLink (stv 1.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "HolmesGrass") (Concept "wet"))))

(EvaluationLink (stv 0.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "HolmesGrass") (Concept "dry"))))

(EvaluationLink (stv 0.9 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "HolmesGrass") (Concept "wet"))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "HolmesGrass") (Concept "dry" (stv 0.1 1)))))

(EvaluationLink (stv 1.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "HolmesGrass") (Concept "wet"))))

(EvaluationLink (stv 0.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "HolmesGrass") (Concept "dry"))))

(EvaluationLink (stv 0.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" ))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "HolmesGrass") (Concept "wet"))))

(EvaluationLink (stv 1.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off"))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "HolmesGrass") (Concept "dry"))))

; P(HG=T|WG=T)

; Evidence: Watson grass is wet
; P(WG = T)
(EvaluationLink (stv 1.0 1)
 (PredicateNode "evidence")
 (AssociativeLink (Concept "WatsonGrass") (Concept "wet")))

; Evidence Holmes grass is wet
; P(HG = T)
(EvaluationLink (stv 1.0 1)
 (PredicateNode "evidence")
 (AssociativeLink (Concept "HolmesGrass") (Concept "wet")))

; Generate Factor Graph

; Define Python Methods
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

def generate_factor_graph():
  print('generate factor graph')
  return ConceptNode('TBD')

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

; initialize Atomspace in Python
(python-call-with-as "set_atomspace" (cog-atomspace))

(display
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: generate_factor_graph")
   (ListLink))))

;; Sample
;
;(EvaluationLink
; (PredicateNode "graph-edge")
; (AndLink (Concept "P4") (Concept "Rain" )))
;
;(EvaluationLink
; (PredicateNode "graph-edge")
; (AndLink (Concept "P2") (Concept "Rain" )))
;
;(EvaluationLink
; (PredicateNode "graph-edge")
; (AndLink (Concept "P2") (Concept "WatsonGrass" )))
;
;(EvaluationLink
; (PredicateNode "factor-arguments-list")
; (ListLink
;  (Concept "P4")
;  (Concept "Rain")))
;
;(EvaluationLink
; (PredicateNode "factor-arguments-list")
; (ListLink
;  (Concept "P2")
;  (Concept "Rain")
;  (Concept "WatsonGrass")))
