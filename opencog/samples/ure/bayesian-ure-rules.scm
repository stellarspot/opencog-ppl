
(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))
(use-modules (opencog distvalue))


;;;;;;;;;;;;;;;
;; Rule base ;;
;;;;;;;;;;;;;;;

;;; modus-ponens-rule ;;;

(define modus-ponens-rule
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
   (GroundedSchemaNode "scm: modus-ponens-formula")
   (ListLink
    (VariableNode "$Y")
    (Implication
     (VariableNode "$X")
     (VariableNode "$Y"))
    (VariableNode "$X")
   )
  )
 )
)

(define modus-ponens-rule-name
 (DefinedSchema "modus-ponens-rule"))

(Define modus-ponens-rule-name modus-ponens-rule)

(define bayesian-rb (Concept "bayesian-rb"))

; (Implication A B) -> B
(define (modus-ponens-formula B IAB A)
 (let*
  ((key (PredicateNode "CDV"))
   (dvA (cog-value A key))
   (dvAB (cog-value IAB key))
   (dvB (cog-cdv-get-unconditional dvAB dvA))
  )
  (cog-set-value! B key dvB)
 )
)

;;; joint-inheritance-introduction-rule ;;;

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

; (Implication A B) -> (Product A B)
(define (joint-introduction-formula PAB IAB A B)
 (let*
  (
    (key (PredicateNode "CDV"))
    (dvA (cog-value A key))
    (dvAB (cog-value IAB key)))
  (cog-set-value! PAB key (cog-cdv-get-joint dvAB dvA))
 )
)

;;; joint-to-conditional-second-rule ;;;

(define joint-to-conditional-second-rule
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
    (Product
     (VariableNode "$X")
     (VariableNode "$Y")))
   (Product
    (VariableNode "$X")
    (VariableNode "$Y")))
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: joint-to-conditional-second-formula")
   (ListLink
    (Implication
     (VariableNode "$Y")
     (VariableNode "$X"))
    (Product
     (VariableNode "$X")
     (VariableNode "$Y"))
    (VariableNode "$X")
    (VariableNode "$Y")
   )
  )
 )
)

(define joint-to-conditional-second-rule-name
 (DefinedSchema "joint-to-conditional-second-rule"))

(Define joint-to-conditional-second-rule-name joint-to-conditional-second-rule)

; (Product A B) -> (Implication B A)
(define (joint-to-conditional-second-formula IBA PAB A B)
; (display "joint-to-conditional-second-formula") (newline)
 (let
  ((key (PredicateNode "CDV"))
   (dvA  (cog-value A  key))
   (dvAandB (cog-value PAB key))
  )
  (cog-set-value! IBA key (cog-dv-divide dvAandB dvA 0))
 )
)

;;; formulas ;;;
(define (has-ure-dv A)
 "
 Return TrueTV iff A has a dv/cdv attached and it is not empty
 "
 (let
  ((dv (cog-value A (PredicateNode "CDV"))))
  (if (equal? dv '())
   (bool->tv #f)
   (if (cog-dv? dv)
    (bool->tv (not (cog-dv-is-empty dv)))
    (bool->tv (not (cog-cdv-is-empty dv)))
   ))))


(define (println msg value)
 (display msg)
 (newline)
 (display value)
 (newline)
)

;;;;;;;;;;
;; URE  ;;
;;;;;;;;;;

(define bayesian-rb (Concept "bayesian-rb"))

;; Add rules to bayesian-rb
(ure-add-rules bayesian-rb
 (list
  (cons joint-inheritance-introduction-rule-name (stv 1.0 1.0))
  (cons joint-to-conditional-second-rule-name (stv 1.0 1.0))
  (cons modus-ponens-rule-name (stv 1.0 1.0))
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
