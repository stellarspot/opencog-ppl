# Generalized Distributional TV

[OpenCog GDTV branch](https://github.com/rTreutlein/atomspace/tree/GDTV)
[Bayesian Net sample](https://github.com/rTreutlein/opencog/tree/DV_Example/examples/pln/dv/dv-bayes-net)

## Simple Rain and Wet Grass Sample

P(R)

|true |false |
|-----|------|
|  0.2|   0.8|

P(WG|R)

|    R|   wet|       dry|
|-----|------|----------|
|true |0.9   |      0.1 |
|false|0.25  |      0.75|


P(WG, R) = P(WG|R) P(R)

```scheme
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
;F - 0.8 , T - 0.2 , Count 100000
(cog-set-value! R key (cog-new-dv zo '(80000 20000)))

;Wet Grass given Rain
;Rain = False
;F - 0.6 , T - 0.4 , Count 80000
;Rain = True
;F - 0.99 , T - 0.01 , Count 20000
;Total Count 100000
(define dvWR0 (cog-new-dv zo '(48000 32000)))
(define dvWR1 (cog-new-dv zo '(19800 200)))

(define dvWR (cog-new-cdv zo (list dvWR0 dvWR1)))
(cog-set-value! WR key dvWR)


(load "pln-config.scm")

;Run Inference manually
(cog-execute! modus-ponens-inheritance-rule)
(cog-execute! joint-inheritance-introduction-rule)
(cog-execute! joint-reduction-rule)
(cog-execute! modus-ponens-inheritance-rule)
(cog-execute! joint-to-inheritance-second-rule)

;Outpute Rain given Wet
(cog-value (Inheritance W R) key)

```