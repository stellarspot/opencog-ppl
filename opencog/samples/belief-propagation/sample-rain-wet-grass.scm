(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))
(use-modules (opencog distvalue))

;;;;;;;;;;;;;;;;;;;;;
;;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;;

(define R (ConceptNode "Rain"))
(define W (ConceptNode "WetGrass"))

; R -> W
(Implication (stv 1 1) R W)

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

;;;;;;;;;;;;;;;;;;;;;;
;; Backward Chainer ;;
;;;;;;;;;;;;;;;;;;;;;;

(load "belief-propagation-ure-rules.scm")

(display
 (cog-execute! init-factor-graph-implication)
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