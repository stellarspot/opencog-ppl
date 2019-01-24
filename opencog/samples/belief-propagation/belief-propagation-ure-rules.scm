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


def get_variable(variable):
    return ConceptNode('Variable-' + variable.name)


def get_factor(variables):
    names = list(map(lambda node: node.name, variables.out))
    names.sort()
    name = '-'.join(names)
    return ConceptNode('Factor-' + name)

")

(python-call-with-as "set_atomspace" (cog-atomspace))

(define (get-variable v)
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: get_variable")
   (ListLink v))))

(define (get-factor variables)
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: get_factor")
   (ListLink variables))))

(define (get-edge factor variable)
 (EvaluationLink
  graph-edge-predicate
  (ListLink factor variable))
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Knowledge Base to Factor Graph  ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define graph-edge-predicate (PredicateNode "graph-edge"))
(define cdv-key (PredicateNode "CDV"))


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
   (factor (get-factor (List v1 v2)))
   (var1 (get-variable v1))
   (var2 (get-variable v2))
  )
  (ListLink
   (get-edge factor var1)
   (get-edge factor var2))
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


;;;;;;;;;;;;;;;
;; Formulas  ;;
;;;;;;;;;;;;;;;

;;; formulas ;;;
(define (has-dv A)
 "
 Return TrueTV iff A has a dv/cdv attached and it is not empty
 "
 (let
  ((dv (cog-value A cdv-key)))
  (if (equal? dv '())
   (bool->tv #f)
   (if (cog-dv? dv)
    (bool->tv (not (cog-dv-is-empty dv)))
    (bool->tv (not (cog-cdv-is-empty dv)))
   ))))


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