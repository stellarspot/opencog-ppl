(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))
(use-modules (opencog distvalue))

;Define the basic concepts
(define R (ConceptNode "Rain"))
(define W (ConceptNode "Grass Wet"))
(define WR (InheritanceLink R W))

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


(load "../distvalues/pln-config.scm")

;Run Inference manually
;(cog-execute! modus-ponens-inheritance-rule)
;(cog-execute! joint-inheritance-introduction-rule)
;(cog-execute! joint-reduction-rule)
;(cog-execute! modus-ponens-inheritance-rule)
;(cog-execute! joint-to-inheritance-second-rule)

;Outpute Rain given Wet
;(cog-value (Inheritance W R) key)

(display "Rain:") (newline)
(display (cog-value R key))

(display (cog-value (Inheritance R W) key))
(newline)

(display "joint-inheritance-introduction-rule:") (newline)
(display (cog-execute! joint-inheritance-introduction-rule))
(display "(Product Rain Sprinkler)") (newline)
(display (cog-value (Product R W) key))
(newline)

(display "modus-ponens-inheritance-rule:") (newline)
(display (cog-execute! modus-ponens-inheritance-rule))

(display (cog-value W key))
(newline)

(display "joint-to-inheritance-second-rule:") (newline)
(display (cog-execute! joint-to-inheritance-second-rule))

;Outpute Rain given Wet Grass
(newline)
(display "Rain given Wet Grass:") (newline)
(display (cog-value (Inheritance W R) key))
