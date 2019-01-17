; see full example https://github.com/opencog/atomspace/blob/master/examples/rule-engine/frog/rule-base.scm
(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))
(use-modules (opencog distvalue))

;; Alternative way of formalizing the frog example. Here the
;; implications are replaced by rules to form the rule base.

;;;;;;;;;;;;;;;;;;;;
;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;

(define R (ConceptNode "Rain"))
(define W (ConceptNode "Grass Wet"))
(define WR (Implication (stv 1.0 1.0) R W))

;Key for the DV Values
(define key (PredicateNode "URE-CDV"))

;Helper simple DVs
;which is a list of DVKey equivalents
;a DVKey consits of a list of Intervals
;which are list of either lenght 1 or 2
(define zo (list (list '(0)) (list '(1))))

;Rain
;F - 0.8 , T - 0.2 , Count 100_0000
(cog-set-value! R key (cog-new-dv zo '(80000 20000)))

;Wet Grass given Rain
;Rain = False
;F - 0.75 , T - 0.25 , Count 100_000
;Rain = True
;F - 0.1 , T - 0.9 , Count 10-_000
;Total Count 100000
(define dvWR0 (cog-new-dv zo '(75000 25000)))
(define dvWR1 (cog-new-dv zo '(10000 90000)))

(define dvWR (cog-new-cdv zo (list dvWR0 dvWR1)))
(cog-set-value! WR key dvWR)

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
   (NotLink
    (EqualLink
     (VariableNode "$X")
     (VariableNode "$Y")))
   (Evaluation
    (GroundedPredicate "scm: has-ure-dv")
    (VariableNode "$X"))
   (Evaluation
    (GroundedPredicate "scm: has-ure-dv")
    (Implication
     (VariableNode "$X")
     (VariableNode "$Y")))

   (Implication
    (VariableNode "$X")
    (VariableNode "$Y")))

  (ExecutionOutputLink
   (GroundedSchemaNode "scm: joint-introduction-formula")
   (ListLink
    (Product
     (VariableNode "$X")
     (VariableNode "$Y"))
    (Implication
     (VariableNode "$X")
     (VariableNode "$Y"))
    (VariableNode "$X")
    (VariableNode "$Y")
   )
  )
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

(define (println msg value)
 (display msg)
 (newline)
 (display value)
 (newline)
)

(define (joint-introduction-formula PAB IAB A B)
  (let*
   (
    (key (PredicateNode "URE-CDV"))
    (dvA  (cog-value A  key))
    (dvAB (cog-value IAB key)))
   (cog-set-value! PAB key (cog-cdv-get-joint dvAB dvA))
  )
; (cog-set-tv! PAB (stv 1 1))
)


(define (has-ure-dv A)
 "
 Return TrueTV iff A has a dv/cdv attached and it is not empty
 "
 (let
  ((dv (cog-value A (PredicateNode "URE-CDV"))))
  (if (equal? dv '())
   (bool->tv #f)
   (if (cog-dv? dv)
    (bool->tv (not (cog-dv-is-empty dv)))
    (bool->tv (not (cog-cdv-is-empty dv)))
   ))))


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


(display (cog-value (Product R W) key))
