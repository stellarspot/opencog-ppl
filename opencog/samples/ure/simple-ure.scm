;;
;; Adapted Frog example from https://github.com/singnet/atomspace/tree/master/examples/rule-engine/frog
;;

(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

;;;;;;;;;;;;;;;;;;;;;
;;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;;


(Inheritance (stv 1.0 1.0) (Concept "A") (Concept "B"))
(Inheritance (stv 1.0 1.0) (Concept "B") (Concept "C"))

(ImplicationScope (stv 1.0 1.0)
 (VariableList
 (TypedVariable (Variable "$X") (Type "ConceptNode"))
 (TypedVariable (Variable "$Y") (Type "ConceptNode"))
 (TypedVariable (Variable "$Z") (Type "ConceptNode")))
 (And
  (Inheritance
   (Variable "$X")
   (Variable "$Y"))
  (Inheritance
   (Variable "$Y")
   (Variable "$Z")))
 (Inheritance
  (Variable "$X")
  (Variable "$Z")))


;;;;;;;;;;;;;;;;;
;; Rule  base  ;;
;;;;;;;;;;;;;;;;;

;; Load the rules (use load for relative path w.r.t. to that file)
(load "../meta-rules/conditional-instantiation-meta-rule.scm")
(load "../meta-rules/fuzzy-conjunction-introduction-rule.scm")


;; Define the rule base ci-rbs by inheriting from the predefined top
;; rule base call "URE"
(define ci-rbs (ConceptNode "ci-rbs"))
(Inheritance ci-rbs (ConceptNode "URE"))

;; Associate the rules to the rule base (with weights, their semantics
;; is currently undefined, we might settled with probabilities but it's
;; not sure)
(MemberLink (stv 1 1)
 conditional-full-instantiation-meta-rule-name
 ci-rbs
)
(MemberLink (stv 1 1)
 fuzzy-conjunction-introduction-2ary-rule-name
 ci-rbs
)

;; termination criteria parameters
(ExecutionLink
 (SchemaNode "URE:maximum-iterations")
 ci-rbs
 (NumberNode "20")
)

;; Attention allocation (set the TV strength to 0 to disable it, 1 to
;; enable it)
(EvaluationLink (stv 0 1)
 (PredicateNode "URE:attention-allocation")
 ci-rbs
)

(cog-execute! fuzzy-conjunction-introduction-2ary-rule)

;(display
; (map cog-execute! (cog-outgoing-set (cog-execute! conditional-full-instantiation-meta-rule))))


;;;;;;;;;;;;;;;;;;;;;;
;; Backward Chainer ;;
;;;;;;;;;;;;;;;;;;;;;;

(display
 (cog-bc
  ci-rbs
  (InheritanceLink (VariableNode "$X") (ConceptNode "C"))
  #:vardecl (TypedVariable (VariableNode "$X") (TypeNode "ConceptNode"))))