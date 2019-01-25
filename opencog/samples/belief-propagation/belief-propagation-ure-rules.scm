(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine) (opencog python))
(use-modules (opencog distvalue))


;;;;;;;;;;;;;;;;
;; Constants  ;;
;;;;;;;;;;;;;;;;

(define graph-edge-predicate (PredicateNode "graph-edge"))
(define cdv-key (PredicateNode "CDV"))
(define variable-predicate (PredicateNode "variable-node"))
(define factor-predicate (PredicateNode "factor-node"))
(define prob-key (ConceptNode "probability"))
(define prob-shape-key (ConceptNode "probability-shape"))

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

def show_dv(atom):
    prob = atom.get_value(ConceptNode('probability'))
    shape = atom.get_value(ConceptNode('probability-shape'))
    print('dv values:', prob, 'shape:', shape)
    return ConceptNode('Test')


def move_value(key, atom_from, atom_to):
    value = atom_from.get_value(key)
    atom_to.set_value(key, value)
    return ConceptNode('Test')

def move_prob_values(atom_from, atom_to):
    move_value(ConceptNode('probability'), atom_from, atom_to)
    move_value(ConceptNode('probability-shape'), atom_from, atom_to)
    return ConceptNode('Test')

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
  (ListLink factor variable)))

(define (get-variable-predicate v)
 (Evaluation
  variable-predicate
  v))

(define (get-factor-predicate f)
 (Evaluation
  factor-predicate
  f))

(define (show-dv v)
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: show_dv")
   (ListLink v))))

(define (move-prob-values a1 a2)
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: move_prob_values")
   (ListLink a1 a2))))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Knowledge Base to Factor Graph  ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


(define init-factor-graph-implication
 (BindLink
  (VariableList
   (TypedVariable (Variable "$V1") (Type "ConceptNode"))
   (TypedVariable (Variable "$V2") (Type "ConceptNode"))
  )
  (And
   ;; Preconditions
   (Evaluation
    (GroundedPredicate "scm: has-dv")
    (Implication
     (Variable "$V1")
     (Variable "$V2"))
   )
   ;; Pattern clauses
   (Implication
    (Variable "$V1")
    (Variable "$V2"))
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


(define (init-factor-graph-implication-formula I v1 v2)
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
  (move-prob-values I factor)
  (show-dv factor)
  (ListLink
   (get-factor-predicate factor)
   (get-variable-predicate var1)
   (get-variable-predicate var2)
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