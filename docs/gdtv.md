# Generalized Distributional TV

* [OpenCog GDTV branch](https://github.com/rTreutlein/atomspace/tree/GDTV)
* [Bayesian Net sample](https://github.com/rTreutlein/opencog/tree/DV_Example/examples/pln/dv/dv-bayes-net)

## Simple Rain and Wet Grass Sample

P(R)

|false|true |
|-----|-----|
|  0.8|  0.2|

P(WG|R)

|R    | dry |wet   |
|-----|-----|------|
|false|0.75 |0.25  |
|true |0.1  |0.9   |


P(WG, R) = P(WG|R) P(R)

P(R=r|WG=wg) = P(R=r, WG=wg) / P(WG=wg) = P(R=r, WG=wg) / (P(WG=wg|R=true) + P(WG=wg|R=false))

|WG   | false|  true|
|-----|------|------|
|dry  |0.88  |  0.12|
|wet  |0.22  |  0.78|


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

Result output:
```scheme
Rain given Wet Grass:
{0} DV:
    {0} Count: 96774.1935483870911 Mean: 0.967741935483870885
    {1} Count: 3225.80645161290295 Mean: 0.0322580645161290314

{1} DV:
    {0} Count: 52631.5789473684199 Mean: 0.526315789473684181
    {1} Count: 47368.4210526315728 Mean: 0.473684210526315708
```