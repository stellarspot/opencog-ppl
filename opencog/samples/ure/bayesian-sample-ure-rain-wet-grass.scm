(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))
(use-modules (opencog distvalue))

;;;;;;;;;;;;;;;;;;;;
;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;


(define R (ConceptNode "Rain"))
(define W (ConceptNode "Grass Wet"))
(define WR (Implication (stv 1.0 1.0) R W))

;Key for the DV Values
(define key (PredicateNode "CDV"))

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

;(define pWR (Product (stv 1.0 1.0) R W))
;(cog-set-value! pWR key dvWR)


(load "bayesian-ure-rules.scm")

(display
 (cog-bc
  bayesian-rb
  W))

(display "Wet Grass:") (newline)
(display (cog-value W key))
(newline)


(display
 (cog-bc
  bayesian-rb
  (Implication (VariableNode "$X") R)
  #:vardecl (TypedVariable (VariableNode "$X") (TypeNode "ConceptNode"))))


(display "Rain given Wet Grass:") (newline)
(display (cog-value (Implication W R) key))
