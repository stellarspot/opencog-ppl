(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))
(use-modules (opencog distvalue))

(load "belief-propagation-ure-rules.scm")

;;;;;;;;;;;;;;;;;;;;;
;;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;;

(define R (ConceptNode "Rain"))
(define W (ConceptNode "WetGrass"))
(define WR (Implication R W))

;; R -> W
;(Implication (stv 1 1) R W)

;Key for the DV Values
(define key (PredicateNode "CDV"))

;Helper simple DVs
;which is a list of DVKey equivalents
;a DVKey consits of a list of Intervals
;which are list of either lenght 1 or 2
(define zo (list (list '(0)) (list '(1))))

;Rain
;F - 0.8 , T - 0.2 , Count 100000
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


(cog-set-value! R prob-key (StringValue "0.2 0.8"))
(cog-set-value! R prob-shape-key (StringValue "2"))

(cog-set-value! W prob-shape-key (StringValue "2"))

(cog-set-value! WR prob-key (StringValue "0.9 0.1 0.25 0.75"))
(cog-set-value! WR prob-shape-key (StringValue "2 2"))

;;;;;;;;;;;;;;;;;;;;;;
;; Backward Chainer ;;
;;;;;;;;;;;;;;;;;;;;;;

;(display R)
;(display key)
;(display (cog-value R key))

;(display
 (cog-execute! init-factor-graph-concept-node)
;)

;(display
 (cog-execute! init-factor-graph-implication)
;)

(display "=== Generate Messages [1] ===\n")

(display
 (cog-execute! message-variable-to-factor)
)

(display
 (cog-execute! message-factor-to-variable)
)

(display "=== show message ===\n")

(show-dv
 (EvaluationLink
  (PredicateNode "message")
  (ConceptNode "Variable-WetGrass")
  (ConceptNode "Factor-Rain-WetGrass")
 )
)

(display "=== Generate Messages [2] ===\n")

(display
 (cog-execute! message-variable-to-factor)
)

;(display
; (cog-bc
;  belief-propagation-rbs
;
;  (EvaluationLink
;   graph-edge-predicate
;   (ListLink (Variable "$X") W))
;
;  #:vardecl (TypedVariable (Variable "$X") (TypeNode "ConceptNode")))
;)