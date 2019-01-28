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
(define prob-arguments-key (ConceptNode "probability-arguments"))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Python utility methods  ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


(python-eval "
from opencog.atomspace import AtomSpace, types, TruthValue

from opencog.utilities import initialize_opencog
from opencog.type_constructors import *
from opencog.bindlink import bindlink
from opencog.bindlink import satisfaction_link


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

# order of factor arguments
# variable names saved with 'probability-arguments' key
def set_factor_arguments(f, arguments_list):
    arguments = list(map(lambda v: v.name, arguments_list.out))
    value = StringValue(arguments)
    f.set_value(ConceptNode('probability-arguments'), value)
    return ConceptNode('Test')


def get_factors(v, exclude_factor):
    bind_link = BindLink(
        VariableNode('$F'),
        AndLink(
            EvaluationLink(
                PredicateNode('factor-node'),
                VariableNode('$F')),
            EvaluationLink(
                PredicateNode('graph-edge'),
                    ListLink(
                        VariableNode('$F'),
                        v
                    )
                ),
             NotLink(
                 EqualLink(
                     exclude_factor,
                     VariableNode('$F')))
        ),
        VariableNode('$F'))

    factors_link = bindlink(atomspace, bind_link)
    return factors_link

def get_variables(f, exclude_variable):
    bind_link = BindLink(
        VariableNode('$V'),
        AndLink(
            EvaluationLink(
                PredicateNode('variable-node'),
                VariableNode('$V')),
            EvaluationLink(
                PredicateNode('graph-edge'),
                    ListLink(
                        f,
                        VariableNode('$V')
                    )
                ),
             NotLink(
                 EqualLink(
                     exclude_variable,
                     VariableNode('$V')))
        ),
        VariableNode('$V'))

    variables_link = bindlink(atomspace, bind_link)
    return variables_link


def get_message(n1, n2):
    return None

def can_send_message_variable_factor(v, f):
    factors = get_factors(v, f)

    for nf in factors.out:
        msg = get_message(nf, v)
        if not msg:
            return TruthValue(0, 0)
    return TruthValue(1, 1)


def can_send_message_factor_variable(f, v):
    variables = get_variables(f, v)

    for nv in variables.out:
        msg = get_message(nv, f)
        if not msg:
            return TruthValue(0, 0)
    return TruthValue(1, 1)


def get_initial_variable_message(shape):
    size = shape.to_list()[0]
    msg = ' '.join(['1'] * int(size))
    return StringValue(msg)

def get_initial_factor_message(f):
    # Factor tensor needs to be converted to message
    value = f.get_value(ConceptNode('probability'))
    msg = value.to_list()
    return StringValue(msg)


def send_message_variable_factor(msg, v, f):
    factors = get_factors(v, f).out

    if len(factors) == 0:
        shape = v.get_value(ConceptNode('probability-shape'))
        msg_value = get_initial_variable_message(shape)
        msg.set_value(ConceptNode('message'), msg_value)
        print('send msg (v-f): ', v.name, f.name, msg_value)

    return ConceptNode('Test')

def send_message_factor_variable(msg, v, f):
    #print('send msg (f-v): ', f.name, v.name)
    variables = get_variables(f, v).out

    if len(variables) == 0:
        msg_value = get_initial_factor_message(f)
        msg.set_value(ConceptNode('message'), msg_value)
        print('send msg (f-v): ', f.name, v.name, msg_value)


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

(define (move-value key a1 a2)
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: move_value")
   (ListLink key a1 a2))))

(define (move-prob-values a1 a2)
 (move-value prob-key a1 a2)
 (move-value prob-shape-key a1 a2)
)

(define (eval-has-dv v)
 (Evaluation
  (GroundedPredicate "scm: has-dv")
  v))

(define (set-factor-arguments f list)
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: set_factor_arguments")
   (ListLink f list))))


(define (can-send-message-variable-factor v f)
 (Evaluation
  (GroundedPredicate "py: can_send_message_variable_factor")
  (ListLink v f)))

(define (can-send-message-factor-variable f v)
 (Evaluation
  (GroundedPredicate "py: can_send_message_factor_variable")
  (ListLink f v)))

(define (send-message-variable-factor M v f)
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: send_message_variable_factor")
   (ListLink M v f))))

;(define (send-message-factor-variable M f v)
; (cog-execute!
;  (ExecutionOutputLink
;   (GroundedSchemaNode "py: send_message_factor_variable")
;   (ListLink M f v))))

(define (send-message-factor-variable M v f)
 (cog-execute!
  (ExecutionOutputLink
   (GroundedSchemaNode "py: send_message_factor_variable")
   (ListLink M f v))))

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
  (move-value prob-shape-key v var)
;  (show-dv factor)
  (set-factor-arguments factor (List var))

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
 (display "init factor graph implication formula:\n")
 (let*
  (
   (factor (get-factor (List v1 v2)))
   (var1 (get-variable v1))
   (var2 (get-variable v2))
  )
  (move-prob-values I factor)
  ; set shape for variables which does not have dv
  (move-value prob-shape-key v1 var1)
  (move-value prob-shape-key v2 var2)
  (set-factor-arguments factor (List var1 var2))
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
;    Predicate "factor-node"
;    F
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
;        Concept F
;----------------------------------------------------------------------

(define message-variable-to-factor
 (BindLink
  (VariableList
   (TypedVariable (Variable "$V") (Type "ConceptNode"))
   (TypedVariable (Variable "$F") (Type "ConceptNode"))
  )
  (And
   ;; Preconditions
   (Absent
    (Evaluation
     message-predicate
     (Variable "$V")
     (Variable "$F")))
   (can-send-message-variable-factor
    (Variable "$V")
    (Variable "$F"))
   ;; Pattern clauses
   (get-variable-predicate (Variable "$V"))
   (get-factor-predicate (Variable "$F"))
   (get-edge (Variable "$F") (Variable "$V"))
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
; (display "message variable to factor formula:\n")
 (send-message-variable-factor M v f)
 M
)

; =====================================================================
; Factor to Variable Message rule
;
; Evaluation
;    Predicate "factor-node"
;    F
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
;        Concept F
;        Concept A
;----------------------------------------------------------------------

(define message-factor-to-variable
 (BindLink
  (VariableList
   (TypedVariable (Variable "$F") (Type "ConceptNode"))
   (TypedVariable (Variable "$V") (Type "ConceptNode"))
  )
  (And
   ;; Preconditions
   (Absent
    (Evaluation
     message-predicate
     (Variable "$F")
     (Variable "$V")))
   (can-send-message-factor-variable
    (Variable "$F")
    (Variable "$V"))
   ;; Pattern clauses
   (get-factor-predicate (Variable "$F"))
   (get-variable-predicate (Variable "$V"))
   (get-edge (Variable "$F") (Variable "$V"))
  )
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: message-factor-to-variable-formula")
   (List
    (Evaluation
     message-predicate
     (Variable "$F")
     (Variable "$V")
    )
    (Variable "$F")
    (Variable "$V"))
  )))


(define (message-factor-to-variable-formula M f v)
; (display "message factor to variable formula:\n")
 (send-message-factor-variable M f v)
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