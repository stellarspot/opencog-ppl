(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

;;;;;;;;;;;;;;;;;;;;
;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;

(define edge-key (Predicate "edge"))
(define message-key (Predicate "message"))

(define node-a (Concept "A"))
(define node-b (Concept "B"))

(define (edge a b)
 (Evaluation (stv 1 1)
  edge-key
  (List a b)))

(define (message a b)
 (Evaluation
  message-key
  (List a b)))


(edge node-a node-b)

;;;;;;;;;;;;;;;
;; Rule base ;;
;;;;;;;;;;;;;;;


(define message-sending-rule

 (Bind
  (VariableList
   (TypedVariable (Variable "$X") (Type "ConceptNode"))
   (TypedVariable (Variable "$Y") (Type "ConceptNode")))
  (edge
   (Variable "$X")
   (Variable "$Y"))
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: message-sending-formula")
   (ListLink
    (message
     (Variable "$X")
     (Variable "$Y"))))))


(define (message-sending-formula M)
 (display "[message-sending-formula]")
 (newline)
 M
)

(define message-sending-rule-name
 (DefinedSchema "message-sending-rule"))

(Define message-sending-rule-name message-sending-rule)

;;;;;;;;;;
;; URE  ;;
;;;;;;;;;;

(define bayesian-rb (Concept "bayesian-rb"))

;; Add rules to bayesian-rb
(ure-add-rules bayesian-rb
 (list
  (cons message-sending-rule-name (stv 1 1))))

;; Set URE parameters
(ure-set-maximum-iterations bayesian-rb 20)


;; Attention allocation (set the TV strength to 0 to disable it, 1 to
;; enable it)
(EvaluationLink (stv 0 1)
 (PredicateNode "URE:attention-allocation")
 bayesian-rb)


(display
 (cog-fc
  bayesian-rb
  (SetLink)))