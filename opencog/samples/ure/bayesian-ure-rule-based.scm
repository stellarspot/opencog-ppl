; see full example https://github.com/opencog/atomspace/blob/master/examples/rule-engine/frog/rule-base.scm
(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

;; Alternative way of formalizing the frog example. Here the
;; implications are replaced by rules to form the rule base.

;;;;;;;;;;;;;;;;;;;;
;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;

(define R (ConceptNode "Rain"))
(define W (ConceptNode "Grass Wet"))
(define WR (Implication (stv 1.0 1.0) R W))

;;;;;;;;;;;;;;;
;; Rule base ;;
;;;;;;;;;;;;;;;


(define joint-inheritance-introduction-rule
 (BindLink
  (VariableList
   (TypedVariable (Variable "$X") (Type "ConceptNode"))
   (TypedVariable (Variable "$Y") (Type "ConceptNode"))
  )
  (And
   (Implication
    (VariableNode "$X")
    (VariableNode "$Y"))
   (NotLink
    (EqualLink
     (VariableNode "$X")
     (VariableNode "$Y")))
  )
  (Product
   (VariableNode "$X")
   (VariableNode "$Y"))
 )
)

(define joint-inheritance-introduction-rule-name
 (DefinedSchema "joint-inheritance-introduction-rule"))

(Define joint-inheritance-introduction-rule-name
 joint-inheritance-introduction-rule)

(define bayesian-rb (Concept "bayesian-rb"))

;; Add rules to bayesian-rb
(ure-add-rules bayesian-rb
 (list
  (cons joint-inheritance-introduction-rule-name (stv 1.0 1.0))
 )
)

;; Set URE parameters
(ure-set-maximum-iterations bayesian-rb 20)


;; Load the rules (use load for relative path w.r.t. to that file)
(load "../meta-rules/conditional-instantiation-meta-rule.scm")
(load "../meta-rules/fuzzy-conjunction-introduction-rule.scm")

;; Associate the rules to the rule base (with weights, their semantics
;; is currently undefined, we might settled with probabilities but it's
;; not sure)
(MemberLink (stv 1.0 1.0)
 conditional-full-instantiation-meta-rule-name
 bayesian-rb
)

(MemberLink (stv 1.0 1.0)
 fuzzy-conjunction-introduction-2ary-rule-name
 bayesian-rb
)

;; Attention allocation (set the TV strength to 0 to disable it, 1 to
;; enable it)
(EvaluationLink (stv 0 1)
 (PredicateNode "URE:attention-allocation")
 bayesian-rb
)

(display
 (cog-bc
  bayesian-rb
  (Product (VariableNode "$X") W)
  #:vardecl (TypedVariable (VariableNode "$X") (TypeNode "ConceptNode"))))
