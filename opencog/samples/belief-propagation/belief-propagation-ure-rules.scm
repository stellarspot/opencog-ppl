(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine) (opencog python))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Python utility methods  ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


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


def get_factor(variables):
    names = list(map(lambda node: node.name, variables.out))
    names.sort()
    name = '-'.join(names)
    return ConceptNode('Factor-' + name)

")

(python-call-with-as "set_atomspace" (cog-atomspace))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Knowledge Base to Factor Graph  ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define graph-edge-predicate (PredicateNode "graph-edge"))

(define init-factor-graph-implication
 (BindLink
  (VariableList
   (TypedVariable (Variable "$V1") (Type "ConceptNode"))
   (TypedVariable (Variable "$V2") (Type "ConceptNode"))
  )
  (Implication
   (Variable "$V1")
   (Variable "$V2")
  )
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: init-factor-graph-implication-formula")
   (List
      (Implication
       (Variable "$V1")
       (Variable "$V2")
      )
      (Variable "$V1")
      (Variable "$V2")
   ))))


(define (init-factor-graph-implication-formula i12 v1 v2)
 (display "init factor graph:\n")
 ; (display i12)
 ;  (display v1)
 ;  (display v2)
 (let*
  (
   (factor
    (cog-execute!
     (ExecutionOutputLink
      (GroundedSchemaNode "py: get_factor")
      (ListLink
       (ListLink v1 v2))))
   )
   (edge1
    (EvaluationLink
     graph-edge-predicate
     (ListLink factor v1))
   )
   (edge2
    (EvaluationLink
     graph-edge-predicate
     (ListLink factor v2))
   )
  )
  (ListLink edge1  edge2)
 )
)


;;;;;;;;;;;;;;;;;
;; Rule  base  ;;
;;;;;;;;;;;;;;;;;

; =====================================================================
; Implication to Edge rule
;
; Implication
;   A
;   B
; A
; |-
; Evaluation
;    Predicate "graph-edge"
;    List
;        A
;        B
;----------------------------------------------------------------------

(define on-top-rule
 (BindLink
  (VariableList
   (TypedVariable (Variable "$V1") (Type "ConceptNode"))
   (TypedVariable (Variable "$V2") (Type "ConceptNode"))
  )
  (Implication
   (Variable "$V1")
   (Variable "$V2")
  )
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: on-top-formula")
   (List
    (EvaluationLink
     graph-edge-predicate
     (ListLink
      (Variable "$V1")
      (Variable "$V2")
     ))
   ))))


(define (on-top-formula h)
 (display "formula input:\n")
 (display h)
; (cog-set-tv! h (cog-new-stv 1, 1))
 h)

(define on-top-rule-name
 (DefinedSchema "on-top-rule"))

(Define on-top-rule-name
 on-top-rule)

;;;;;;;;;;
;; URE  ;;
;;;;;;;;;;

(define belief-propagation-rbs (Concept "belief-propagation-rbs"))

;; Add rules to belief-propagation-rbs
(ure-add-rules belief-propagation-rbs
 (list
  (cons on-top-rule-name (stv 1 1))))

;; Set URE parameters
(ure-set-maximum-iterations belief-propagation-rbs 20)

;; Attention allocation (set the TV strength to 0 to disable it, 1 to
;; enable it)
(EvaluationLink (stv 0 1)
 (PredicateNode "URE:attention-allocation")
 belief-propagation-rbs
)