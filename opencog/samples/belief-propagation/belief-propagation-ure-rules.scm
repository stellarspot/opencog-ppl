(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine) (opencog python))
(use-modules (opencog distvalue))


;;;;;;;;;;;;;;;;
;; Constants  ;;
;;;;;;;;;;;;;;;;

(define graph-edge-predicate (PredicateNode "graph-edge"))
(define cdv-key (PredicateNode "CDV"))
(define variable-predicate (PredicateNode "variable-node"))
(define factor-predicate (PredicateNode "factor-node"))
(define message-predicate (PredicateNode "message"))
(define prob-key (ConceptNode "probability"))
(define prob-shape-key (ConceptNode "probability-shape"))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Python utility methods  ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


(python-eval "
from opencog.atomspace import AtomSpace, types, TruthValue

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *
from opencog.bindlink import bindlink


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


def get_factors(exclude_factor):
    bind_link = BindLink(
        VariableNode('$F'),
        AndLink(
            EvaluationLink(
                PredicateNode('factor-node'),
                VariableNode('$F')),
             NotLink(
                 EqualLink(
                     exclude_factor,
                     VariableNode('$F')))
        ),
        VariableNode('$F'))

    factors_link = bindlink(atomspace, bind_link)
    print('factors', factors_link)
    return factors_link


def can_send_message_variable_factor(v, f):
    print('can_send_message_variable_factor')
    #print('variable', v)
    print('factor', f)
    factors = get_factors(f)
    print('factors', f)
    return TruthValue(1, 1)


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


(define (eval-has-dv v)
 (Evaluation
  (GroundedPredicate "scm: has-dv")
  v))

(define (can-send-message-variable-factor v f)
 (Evaluation
  (GroundedPredicate "py: can_send_message_variable_factor")
  (ListLink v f)
 )
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Knowledge Base to Factor Graph  ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; =====================================================================
; ConceptNode to Variable rule
;
; A
; |-
; Evaluation
;    Predicate "factor-node"
;    Concept "Factor-A"
;
; Evaluation
;    Predicate "variable-node"
;    Concept "Variable-A"
;
; Evaluation
;    Predicate "graph-edge"
;    List
;        Concept "Factor-A"
;        Concept "Variable-A"
;----------------------------------------------------------------------


(define init-factor-graph-concept-node
 (BindLink
  (TypedVariable (Variable "$V") (Type "ConceptNode"))
  (eval-has-dv (Variable "$V"))
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: init-factor-graph-concept-node-formula")
   (List
      (Variable "$V")))
 ))


(define (init-factor-graph-concept-node-formula v)
 (display "init factor graph conept node formula:\n")
 (let*
  (
    (factor (get-factor (List v)))
    (var (get-variable v))
  )
  (move-prob-values v factor)
  (show-dv factor)

  (ListLink
   (get-factor-predicate factor)
   (get-variable-predicate var)
   (get-edge factor var)
  )
 )
)

; =====================================================================
; Implication to Variable rule
;
; Implication
;   A
;   B
; |-
; Evaluation
;    Predicate "factor-node"
;    Concept "Factor-A-b"
;
; Evaluation
;    Predicate "variable-node"
;    Concept "Variable-A"
;
; Evaluation
;    Predicate "variable-node"
;    Concept "Variable-B"
;
; Evaluation
;    Predicate "graph-edge"
;    List
;        Concept "Factor-A-B"
;        Concept "Variable-A"
;
; Evaluation
;    Predicate "graph-edge"
;    List
;        Concept "Factor-A-B"
;        Concept "Variable-B"
;----------------------------------------------------------------------


(define init-factor-graph-implication
 (BindLink
  (VariableList
   (TypedVariable (Variable "$V1") (Type "ConceptNode"))
   (TypedVariable (Variable "$V2") (Type "ConceptNode"))
  )
  (And
   ;; Preconditions
   (eval-has-dv
    (Implication
     (Variable "$V1")
     (Variable "$V2")))
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
      (Variable "$V2"))
  )))


(define (init-factor-graph-implication-formula I v1 v2)
 (display "init factor graph implication formuls:\n")
 (let*
  (
   (factor (get-factor (List v1 v2)))
   (var1 (get-variable v1))
   (var2 (get-variable v2))
  )
  (move-prob-values I factor)
;  (show-dv factor)
  (ListLink
   (get-factor-predicate factor)
   (get-variable-predicate var1)
   (get-variable-predicate var2)
   (get-edge factor var1)
   (get-edge factor var2))
 )
)


; =====================================================================
; Variable to Factor Message rule
;
; Evaluation
;    Predicate "variable-node"
;    A
; Evaluation
;    Predicate "graph-edge"
;    List
;        Concept F
;        Concept A
; |-
;
; Evaluation
;    Predicate "graph-message"
;    List
;        Concept A
;        Concept F"
;----------------------------------------------------------------------

(define message-variable-to-factor
 (BindLink
  (VariableList
   (TypedVariable (Variable "$V") (Type "ConceptNode"))
   (TypedVariable (Variable "$F") (Type "ConceptNode"))
  )
  (And
   ;; Preconditions
   ;; Pattern clauses
   (get-variable-predicate (Variable "$V"))
   (get-edge (Variable "$F") (Variable "$V"))
    (Absent
     (Evaluation
      message-predicate
      (Variable "$V")
      (Variable "$F")))
   (can-send-message-variable-factor
    (Variable "$V")
    (Variable "$F"))
  )
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: message-variable-to-factor-formula")
   (List
    (Evaluation
     message-predicate
     (Variable "$V")
     (Variable "$F")
    )
    (Variable "$V")
    (Variable "$F"))
  )))


(define (message-variable-to-factor-formula M v f)
 (display "message variable to formula:\n")
; (display "input:\n")
; (display M)
; (let*
;  (
;   (factor (get-factor (List v1 v2)))
;   (var1 (get-variable v1))
;   (var2 (get-variable v2))
;  )
;  (move-prob-values I factor)
;  ;  (show-dv factor)
;  (ListLink
;   (get-factor-predicate factor)
;   (get-variable-predicate var1)
;   (get-variable-predicate var2)
;   (get-edge factor var1)
;   (get-edge factor var2))
; )
 M
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