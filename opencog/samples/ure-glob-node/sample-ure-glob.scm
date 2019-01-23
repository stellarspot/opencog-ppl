(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

; GlobNode is not supported by URE right now.
; See #2010 Add GlobNode support to the unifier:
;   https://github.com/opencog/atomspace/issues/2010

;;;;;;;;;;;;;;;;;;;;;
;;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;;

(Product (stv 1 1) ; a non-zero truth value is needed!
 (ConceptNode "A")
 (ConceptNode "B"))

;;;;;;;;;;;;;;;;;
;; Rule  base  ;;
;;;;;;;;;;;;;;;;;

(define (on-top-formula h)
 (display "on-top input:\n")
 (display h)
 (cog-set-tv! h (cog-new-stv 0.75 0.42))
 h)

(define on-top-rule
 (BindLink
  (VariableList
   (GlobNode "$X1")
   (TypedVariable (Variable "$X2") (Type "ConceptNode"))
  )
  (Product
   (GlobNode "$X1")
   (Variable "$X2")
  )
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: on-top-formula")
   (List
    (Product
     (Variable "$X2")
     (GlobNode "$X1")
    )))))


(define on-top-rule-name
 (DefinedSchema "on-top-rule"))

(Define on-top-rule-name
 on-top-rule)

;;;;;;;;;;
;; URE  ;;
;;;;;;;;;;

(define ci-rbs (Concept "ci-rbs"))

;; Add rules to ci-rbs
(ure-add-rules ci-rbs
 (list
  (cons on-top-rule-name (stv 1.0 1.0))))

;; Set URE parameters
(ure-set-maximum-iterations ci-rbs 20)

;; Attention allocation (set the TV strength to 0 to disable it, 1 to
;; enable it)
(EvaluationLink (stv 0 1)
 (PredicateNode "URE:attention-allocation")
 ci-rbs
)

;;;;;;;;;;;;;;;;;;;;;;
;; Backward Chainer ;;
;;;;;;;;;;;;;;;;;;;;;;


(display
 (cog-bc
  ci-rbs
  (Product (VariableNode "$X") (Concept "A"))
  #:vardecl (TypedVariable (VariableNode "$X") (TypeNode "ConceptNode")))
)