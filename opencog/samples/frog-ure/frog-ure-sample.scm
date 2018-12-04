;;
;; Frog example from https://github.com/singnet/atomspace/tree/master/examples/rule-engine/frog
;;

;; To be loaded first
(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

;;;;;;;;;;;;;;;;;;;;
;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;

(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

(ImplicationScope (stv 1.0 1.0)
 (TypedVariable
  (Variable "$X")
  (Type "ConceptNode"))
 (And
  (Evaluation
   (Predicate "croaks")
   (Variable "$X"))
  (Evaluation
   (Predicate "eats_flies")
   (Variable "$X")))
 (Inheritance
  (Variable "$X")
  (Concept "frog")))

(ImplicationScope (stv 1.0 1.0)
 (TypedVariable
  (Variable "$X")
  (Type "ConceptNode"))
 (And
  (Evaluation
   (Predicate "chirps")
   (Variable "$X"))
  (Evaluation
   (Predicate "sings")
   (Variable "$X")))
 (Inheritance
  (Variable "$X")
  (Concept "Canary")))

(ImplicationScope (stv 1.0 1.0)
 (TypedVariable
  (Variable "$X")
  (Type "ConceptNode"))
 (Inheritance
  (Variable "$X")
  (Concept "frog"))
 (Inheritance
  (Variable "$X")
  (Concept "green")))

(ImplicationScope (stv 1.0 1.0)
 (TypedVariable
  (Variable "$X")
  (Type "ConceptNode"))
 (Inheritance
  (Variable "$X")
  (Concept "Canary"))
 (Inheritance
  (Variable "$X")
  (Concept "yellow")))

(Evaluation (stv 1.0 1.0)
 (Predicate "croaks")
 (Concept "Fritz"))

(Evaluation (stv 1.0 1.0)
 (Predicate "chirps")
 (Concept "Tweety"))

(Inheritance (stv 1.0 1.0)
 (Concept "Tweety")
 (Concept "yellow"))

(Evaluation (stv 1.0 1.0)
 (Predicate "eats_flies")
 (Concept "Tweety"))

(Evaluation (stv 1.0 1.0)
 (Predicate "eats_flies")
 (Concept "Fritz"))


;;;;;;;;;;;;;;;;;
;; Rule  base  ;;
;;;;;;;;;;;;;;;;;

;; Load the rules (use load for relative path w.r.t. to that file)
(load "./meta-rules/conditional-instantiation-meta-rule.scm")
(load "./meta-rules/fuzzy-conjunction-introduction-rule.scm")

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

(display
 (map cog-execute! (cog-outgoing-set (cog-execute! conditional-full-instantiation-meta-rule))))
