
(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))
(use-modules (opencog distvalue))


;;;;;;;;;;;;;;;
;; Rule base ;;
;;;;;;;;;;;;;;;

;;; modus-ponens-rule ;;;

; (Implication A B) -> B

(define modus-ponens-rule
 (BindLink
  (VariableList
   (TypedVariable (Variable "$X") (Type "ConceptNode"))
   (TypedVariable (Variable "$Y") (Type "ConceptNode"))
  )
  (And
   ;; Preconditions
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
   ;; Pattern clauses
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

(define (modus-ponens-formula B IAB A)
 (display "[modus-ponens-formula] (Implication A B) -> B") (newline)
 (let*
  ((key (PredicateNode "CDV"))
   (dvA (cog-value A key))
   (dvAB (cog-value IAB key))
   (dvB (cog-cdv-get-unconditional dvAB dvA))
  )
  (cog-set-value! B key dvB)
 )
)

(define modus-ponens-rule-name
 (DefinedSchema "modus-ponens-rule"))

(Define modus-ponens-rule-name modus-ponens-rule)

;;; joint-introduction-rule ;;;

; (Implication A B) -> (Product A B)

(define joint-introduction-rule
 (BindLink
  (VariableList
   (TypedVariable (Variable "$X") (Type "ConceptNode"))
   (TypedVariable (Variable "$Y") (Type "ConceptNode"))
  )
  (And
   ;; Preconditions
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
   ;; Pattern clauses
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

(define joint-introduction-rule-name
 (DefinedSchema "joint-introduction-rule"))

(Define joint-introduction-rule-name
 joint-introduction-rule)

(define (joint-introduction-formula PAB IAB A B)
 (display "[joint-introduction-formula] (Implication A B) -> (Product A B)") (newline)
 (println "PAB" PAB)
 (let*
  (
    (key (PredicateNode "CDV"))
    (dvA (cog-value A key))
    (dvAB (cog-value IAB key)))
  (cog-set-value! PAB key (cog-cdv-get-joint dvAB dvA))
  (cog-set-tv! PAB (stv 1.0 1.0))
 )
)
;;; joint-product-introduction-rule ;;;

; (Implication A B) -> (Product A B)

(define joint-product-introduction-rule
 (BindLink
  (VariableList
   (GlobNode "$Xs")
;   (TypedVariable (Variable "$X") (Type "ConceptNode"))
   (TypedVariable (Variable "$Y") (Type "ConceptNode"))
  )
  (And
   ;; Preconditions
   (Evaluation
    (GroundedPredicate "scm: has-ure-dv")
    (Product
     (GlobNode "$Xs")))
   (Evaluation
    (GroundedPredicate "scm: has-ure-dv")
    (Implication
     (Product
      (GlobNode "$Xs"))
     (VariableNode "$Y")))
   ;; Pattern clauses
   (Implication
    (GlobNode "$Xs")
    (VariableNode "$Y")))
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: joint-product-introduction-formula")
   (ListLink
    (Product
     (GlobNode "$Xs")
     (VariableNode "$Y"))
    (Implication
     (Product
      (GlobNode "$Xs"))
     (VariableNode "$Y"))
    (GlobNode "$Xs")
    (VariableNode "$Y")
   )
  )
 )
)

(define joint-product-introduction-rule-name
 (DefinedSchema "joint-product-introduction-rule"))

(Define joint-product-introduction-rule-name
 joint-product-introduction-rule)

(define (joint-product-introduction-formula PAsB IAsB As B)
 (display "[joint-product-introduction-formula] (Implication (Product As) B) -> (Product As B)") (newline)
 (println "PAsB" PAsB)
 (let*
  (
    (key (PredicateNode "CDV"))
    (dvA (cog-value A key))
    (dvAB (cog-value IAsB key)))
  (cog-set-value! PAsB key (cog-cdv-get-joint dvAB dvA))
  (cog-set-tv! PAsB (stv 1.0 1.0))
 )
)

;;; joint-to-conditional-second-rule ;;;

; (Product A B) -> (Implication B A)

(define joint-to-conditional-second-rule
 (BindLink
  (VariableList
   (TypedVariable (Variable "$X") (Type "ConceptNode"))
   (TypedVariable (Variable "$Y") (Type "ConceptNode"))
  )
  (And
   ;; Preconditions
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
   ;; Pattern clauses
;   (VariableNode "$X")
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

(define (joint-to-conditional-second-formula IBA PAB A B)
 (display "[joint-to-conditional-second-formula] (Product A B) -> (Implication B A)") (newline)
 (let
  ((key (PredicateNode "CDV"))
   (dvA  (cog-value A  key))
   (dvAandB (cog-value PAB key))
  )
  (cog-set-value! IBA key (cog-dv-divide dvAandB dvA 0))
 )
)

(define joint-to-conditional-second-rule-name
 (DefinedSchema "joint-to-conditional-second-rule"))

(Define joint-to-conditional-second-rule-name joint-to-conditional-second-rule)

;;; joint-reduction-rule ;;;

; Product(As B Cs) -> Product(As Cs)

(define joint-reduction-rule
 (BindLink
  (VariableList
   (GlobNode "$A")
   (VariableNode "$B")
   (GlobNode "$C")
  )
  (AndLink
   ;; Preconditions
   (Evaluation
    (GroundedPredicate "scm: has-dv")
    (ProductLink
     (GlobNode "$A")
     (VariableNode "$B")
     (GlobNode "$C"))
   )
   ;; Pattern clauses
   (ProductLink
    (GlobNode "$A")
    (VariableNode "$B")
    (GlobNode "$C"))
  )
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: joint-reduction-formula")
   (ListLink
    (Product
     (GlobNode "$A")
     (GlobNode "$C")
    )
    (GlobNode "$A")
    (VariableNode "$B")
    (GlobNode "$C")
    (ProductLink
     (GlobNode "$A")
     (VariableNode "$B")
     (GlobNode "$C")
    )
   )
  )
 )
)

(define joint-reduction-rule-name
 (DefinedSchemaNode "joint-reduction-rule"))

(DefineLink
 joint-reduction-rule-name
 joint-reduction-rule)

(define (joint-reduction-formula PsACs As B Cs AsBCs)
 (display "[joint-reduction-formula] Product(As B Cs) -> Product(As Cs)")
; (println "PsACs" PsACs)
 (let*
  ((key (PredicateNode "CDV"))
   (dvAsBCs (cog-value AsBCs key))
   (lAs (if (cog-link? As)
         (cog-outgoing-set As)
         (list As)
   ))
   (lCs (if (cog-link? As)
         (cog-outgoing-set Cs)
         (list Cs)
   ))
   (lACs (append lAs lCs))
   (i (length lAs))
  )
  (cog-set-value! (ProductLink lACs) key (cog-dv-sum-joint dvAsBCs i))
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
  (cons joint-introduction-rule-name (stv 1.0 1.0))
;  (cons joint-product-introduction-rule-name (stv 1.0 1.0))
  (cons joint-to-conditional-second-rule-name (stv 1.0 1.0))
  (cons joint-reduction-rule-name (stv 1.0 1.0))
  (cons modus-ponens-rule-name (stv 1.0 1.0))
 )
)

;; Set URE parameters
(ure-set-maximum-iterations bayesian-rb 20)

;; Load the rules (use load for relative path w.r.t. to that file)
;(load "../meta-rules/conditional-instantiation-meta-rule.scm")
;(load "../meta-rules/fuzzy-conjunction-introduction-rule.scm")

;; Associate the rules to the rule base (with weights, their semantics
;; is currently undefined, we might settled with probabilities but it's
;; not sure)
;(MemberLink (stv 1.0 1.0)
; conditional-full-instantiation-meta-rule-name
; bayesian-rb
;)

;(MemberLink (stv 1.0 1.0)
; fuzzy-conjunction-introduction-2ary-rule-name
; bayesian-rb
;)

;; Attention allocation (set the TV strength to 0 to disable it, 1 to
;; enable it)
(EvaluationLink (stv 0 1)
 (PredicateNode "URE:attention-allocation")
 bayesian-rb
)
