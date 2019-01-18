;(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))
(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

(use-modules (opencog distvalue))

;Define the basic concepts
(define R (ConceptNode "Rain"))
(define S (ConceptNode "Sprinkler"))
(define W (ConceptNode "Grass Wet"))
(define SR (InheritanceLink R S))
(define WRS (InheritanceLink (ProductLink R S) W))

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

;Spinkler given Rain
;Rain = False
;F - 0.6 , T - 0.4 , Count 80000
;Rain = True
;F - 0.99 , T - 0.01 , Count 20000
;Total Count 100000
(define dvSR0 (cog-new-dv zo '(48000 32000)))
(define dvSR1 (cog-new-dv zo '(19800 200)))

(define dvSR (cog-new-cdv zo (list dvSR0 dvSR1)))
(cog-set-value! SR key dvSR)

;Wet given Rain and Sprinkler
;Rain = False , Sprikler False
;F - 1 , T - 0 , Count 48000
;Rain = True , Sprikler False
;F - 0.2 , T - 0.8 , Count 32000
;Rain = False , Sprikler True
;F - 0.1 , T - 0.9 , Count 19800
;Rain = True , Sprikler True
;F - 0.01 , T - 0.99 , Count 200
;Total Count 100000
(define conds (list (list '(0) '(0))
               (list '(0) '(1))
               (list '(1) '(0))
               (list '(1) '(1))
)
)

(define dvWRS00 (cog-new-dv (list (list '(0))) '(48000)))
(define dvWRS01 (cog-new-dv zo '(3200 28800)))
(define dvWRS10 (cog-new-dv zo '(3960 15840)))
(define dvWRS11 (cog-new-dv zo '(2 198)))

(define dvWRS (cog-new-cdv conds (list dvWRS00 dvWRS01 dvWRS10 dvWRS11)))
(cog-set-value! WRS key dvWRS)

(load "pln-config.scm")

(display "Input:") (newline)
(display "Rain") (newline)
(display (cog-value R key))
(display "(Inheritance Rain Sprinkler)") (newline)
(display (cog-value SR key))
(display "(Inheritance (Product Rain Sprinkler) WetGrass)") (newline)
(display (cog-value WRS key))
(newline)

(display "modus-ponens-inheritance-rule:") (newline)
(display (cog-execute! modus-ponens-inheritance-rule))
(display "Sprinkler:") (newline)
(display (cog-value S key))
(display "-----------------------") (newline)
(newline)

(display "joint-inheritance-introduction-rule:") (newline)
(display (cog-execute! joint-inheritance-introduction-rule))
(display "(Product Rain Sprinkler)") (newline)
(display (cog-value (Product R S) key))
(newline)
(display "(Product Rain Sprinkler WetGrass)") (newline)
(display (cog-value (Product R S W) key))
(display "-----------------------") (newline)
(newline)

(display "joint-reduction-rule:") (newline)
(display (cog-execute! joint-reduction-rule))
(display "-----------------------") (newline)
(newline)
(display "modus-ponens-inheritance-rule:") (newline)
(display (cog-execute! modus-ponens-inheritance-rule))
(display "-----------------------") (newline)
(newline)
(display "joint-to-inheritance-second-rule:") (newline)
(display (cog-execute! joint-to-inheritance-second-rule))

;Outpute Rain given Wet
(newline)
(display "Rain given Wet:") (newline)
(display (cog-value (Inheritance W R) key))


;(display
; (cog-bc
;  (ConceptNode "PLN")
;  (InheritanceLink (VariableNode "$who") (ConceptNode "mortal"))
;  #:vardecl (TypedVariableLink (VariableNode "$who") (TypeNode "ConceptNode"))))
