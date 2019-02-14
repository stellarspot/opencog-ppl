(use-modules (opencog) (opencog exec) (opencog rule-engine))

;; =============================================================================
;; Crisp logic entailment (Deduction) Rule.
;;
;;   A->B
;;   B->C
;;   |-
;;   A->C
;;
;; See examples/rule-engine/README.md for more details.
;; -----------------------------------------------------------------------------

(define fc-deduction-rule
 (BindLink
  (VariableList
   (TypedVariableLink
    (VariableNode "$A")
    (TypeNode "ConceptNode"))
   (TypedVariableLink
    (VariableNode "$B")
    (TypeNode "ConceptNode"))
   (TypedVariableLink
    (VariableNode "$C")
    (TypeNode "ConceptNode")))
  (AndLink
   (InheritanceLink
    (VariableNode "$A")
    (VariableNode "$B"))
   (InheritanceLink
    (VariableNode "$B")
    (VariableNode "$C"))
   ;; To avoid matching (Inheritance A B) and (Inheritance B A)
   (NotLink
    (IdenticalLink
     (VariableNode "$A")
     (VariableNode "$C"))))
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: fc-deduction-formula")
   (ListLink
    (InheritanceLink
     (VariableNode "$A")
     (VariableNode "$C"))
    (InheritanceLink
     (VariableNode "$A")
     (VariableNode "$B"))
    (InheritanceLink
     (VariableNode "$B")
     (VariableNode "$C"))))))


;; -----------------------------------------------------------------------------
;; Deduction Formula
;;
;; If both confidence and strength of A->B and B->C are above 0.5 then
;; set the TV of A->C to (stv 1 1)
;; -----------------------------------------------------------------------------

(define (fc-deduction-formula AC AB BC)
 (let (
       (sAB (cog-stv-strength AB))
       (cAB (cog-stv-confidence AB))
       (sBC (cog-stv-strength BC))
       (cBC (cog-stv-confidence BC)))
  (if (and (>= sAB 0.5) (>= cAB 0.5) (>= sBC 0.5) (>= cBC 0.5))
   (cog-set-tv! AC (stv 1 1)))))

;; Associate a name to the rule
(define fc-deduction-rule-name
 (DefinedSchemaNode "fc-deduction-rule"))

(DefineLink
 fc-deduction-rule-name
 fc-deduction-rule)


;;;;;;;;;;;;;;;;
;; Load rules ;;
;;;;;;;;;;;;;;;;

;; Define a new rule base (aka rule-based system)
(define fc-deduction-rbs (ConceptNode "fc-deduction-rule-base"))
(InheritanceLink
 fc-deduction-rbs
 (ConceptNode "URE"))

;; Associate the rules to the rule base (with weights, their semantics
;; is currently undefined, we might settled with probabilities but it's
;; not sure)
(ure-add-rules fc-deduction-rbs (list fc-deduction-rule-name))

;; Termination criteria parameters
(ure-set-num-parameter fc-deduction-rbs "URE:maximum-iterations" 20)

;; Attention allocation (set the TV strength to 0 to disable it, 1 to
;; enable it)
(ure-set-fuzzy-bool-parameter fc-deduction-rbs "URE:attention-allocation" 0)

;;;;;;;;;;;;;;;;;;;;
;; Knowledge Base ;;
;;;;;;;;;;;;;;;;;;;;

(define A (ConceptNode "A" (stv 1 1)))
(define B (ConceptNode "B"))
(define C (ConceptNode "C"))
(define AB (InheritanceLink (stv 1 1) A B))
(define BC (InheritanceLink (stv 1 1) B C))

;;;;;;;;;;;;;;;;;;;;;
;; Forward Chainer ;;
;;;;;;;;;;;;;;;;;;;;;

(display
 (cog-bc
  fc-deduction-rbs
  (InheritanceLink (VariableNode "$X") C)
  #:vardecl (TypedVariable (VariableNode "$X") (TypeNode "ConceptNode"))))
