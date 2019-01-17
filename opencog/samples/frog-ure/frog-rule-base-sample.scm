; see full example https://github.com/opencog/atomspace/blob/master/examples/rule-engine/frog/rule-base.scm
(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

;; Alternative way of formalizing the frog example. Here the
;; implications are replaced by rules to form the rule base.

;;;;;;;;;;;;;;;;;;;;
;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;

(Evaluation (stv 1.0 1.0)
 (Predicate "croaks")
 (Concept "Fritz"))

(Evaluation (stv 1.0 1.0)
 (Predicate "eats_flies")
 (Concept "Fritz"))


;;;;;;;;;;;;;;;
;; Rule base ;;
;;;;;;;;;;;;;;;

;; In this example the implication relationships are directly
;; represented as rules.

(define if-croaks-and-eats-flies-then-frog-rule
 (BindLink
  (Variable "$X")
  (And
   (Evaluation
    (Predicate "croaks")
    (Variable "$X"))
   (Evaluation
    (Predicate "eats_flies")
    (Variable "$X")))
  (Inheritance
   (Variable "$X")
   (Concept "frog"))))

(define if-croaks-and-eats-flies-then-frog-rule-name
 (DefinedSchema "if-croaks-and-eats-flies-then-frog-rule"))

(Define if-croaks-and-eats-flies-then-frog-rule-name
 if-croaks-and-eats-flies-then-frog-rule)

(define if-frog-then-green-rule
 (Bind
  (Variable "$X")
  (Inheritance
   (Variable "$X")
   (Concept "frog")
  )
  (Inheritance
   (Variable "$X")
   (Concept "green")
  )
 )
)

(define if-frog-then-green-rule-name
 (DefinedSchema "if-frog-then-green-rule"))
(Define if-frog-then-green-rule-name
 if-frog-then-green-rule)

(define frog-rb (Concept "frog-rb"))

;; Add rules to frog-rb
(ure-add-rules frog-rb
 (list
  (cons if-croaks-and-eats-flies-then-frog-rule-name (stv 0.9 1))
  (cons if-frog-then-green-rule-name (stv 0.5 1))))

;; Set URE parameters
(ure-set-maximum-iterations frog-rb 20)


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
(MemberLink (stv 1.0 1.0)
 conditional-full-instantiation-meta-rule-name
 frog-rb
)

(MemberLink (stv 1.0 1.0)
 fuzzy-conjunction-introduction-2ary-rule-name
 frog-rb
)

;; Attention allocation (set the TV strength to 0 to disable it, 1 to
;; enable it)
(EvaluationLink (stv 0 1)
 (PredicateNode "URE:attention-allocation")
 frog-rb
)

(display
 (cog-bc
  frog-rb
  (Inheritance (Concept "Fritz") (VariableNode "$X"))
  #:vardecl (TypedVariable (VariableNode "$X") (TypeNode "ConceptNode"))))
