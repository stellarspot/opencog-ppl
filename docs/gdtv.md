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

P(R=r|WG=wg) = P(R=r, WG=wg) / P(WG=wg)   
P(R=r|WG=wg) = P(R=r, WG=wg) / (P(WG=wg,R=true) + P(WG=wg,R=false))  
P(R=r|WG=wg) = P(WG=wg|R=r) P(R=r) / (P(WG=wg | R=true) P(R=true) + P(WG=wg | R=false) P(R=false))

|WG   | false|  true|
|-----|------|------|
|dry  |0.97  |  0.03|
|wet  |0.53  |  0.47|

[Original OpenCog sample](https://github.com/rTreutlein/opencog/blob/DV_Example/examples/pln/dv/dv-bayes-net/bayesnet.scm)

Updated sample which prints intermidiate steps:

```scheme
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

Detailed result output:
```scheme
Input:
Rain
{0} Count: 80000 Mean: 0.800000000000000044
{1} Count: 20000 Mean: 0.200000000000000011
(Inheritance Rain Sprinkler)
{0} DV: 
    {0} Count: 48000 Mean: 0.599999999999999978
    {1} Count: 32000 Mean: 0.400000000000000022

{1} DV: 
    {0} Count: 19800 Mean: 0.989999999999999991
    {1} Count: 200 Mean: 0.0100000000000000002

(Inheritance (Product Rain Sprinkler) WetGrass)
{0;0} DV: 
    {0} Count: 48000 Mean: 1

{0;1} DV: 
    {0} Count: 3200 Mean: 0.100000000000000006
    {1} Count: 28800 Mean: 0.900000000000000022

{1;0} DV: 
    {0} Count: 3960 Mean: 0.200000000000000011
    {1} Count: 15840 Mean: 0.800000000000000044

{1;1} DV: 
    {0} Count: 2 Mean: 0.0100000000000000002
    {1} Count: 198 Mean: 0.989999999999999991


modus-ponens-inheritance-rule:
(SetLink
   (ConceptNode "Sprinkler")
)
Sprinkler:
{0} Count: 42360 Mean: 0.62294117647058822
{1} Count: 25640 Mean: 0.37705882352941178
-----------------------

joint-inheritance-introduction-rule:
(SetLink
   (ProductLink
      (ConceptNode "Rain")
      (ConceptNode "Sprinkler")
   )
   (ProductLink
      (ConceptNode "Rain")
      (ConceptNode "Sprinkler")
      (ConceptNode "Grass Wet")
   )
)
(Product Rain Sprinkler)
{0;0} Count: 48000 Mean: 0.479999999999999982
{0;1} Count: 32000 Mean: 0.320000000000000007
{1;0} Count: 19800 Mean: 0.198000000000000009
{1;1} Count: 200 Mean: 0.00200000000000000004

(Product Rain Sprinkler WetGrass)
{0;0;0} Count: 48000 Mean: 0.479999999999999982
{0;1;0} Count: 3200 Mean: 0.0320000000000000007
{0;1;1} Count: 28800 Mean: 0.287999999999999978
{1;0;0} Count: 3960 Mean: 0.0396000000000000033
{1;0;1} Count: 15840 Mean: 0.158400000000000013
{1;1;0} Count: 2 Mean: 2.00000000000000016e-05
{1;1;1} Count: 198 Mean: 0.00197999999999999999
-----------------------

joint-reduction-rule:
(SetLink
   (ProductLink
      (ConceptNode "Rain")
      (ConceptNode "Grass Wet")
   )
)
-----------------------

modus-ponens-inheritance-rule:
(SetLink
   (ConceptNode "Sprinkler")
   (ConceptNode "Grass Wet")
)
-----------------------

joint-to-inheritance-second-rule:
(SetLink
   (InheritanceLink
      (ConceptNode "Grass Wet")
      (ConceptNode "Rain")
   )
   (InheritanceLink
      (ConceptNode "Sprinkler")
      (ConceptNode "Rain")
   )
)

Rain given Wet:
{0} DV: 
    {0} Count: 28515.5408589121034 Mean: 0.928175193067691584
    {1} Count: 2206.61275162128413 Mean: 0.0718248069323084715

{1} DV: 
    {0} Count: 32265.2169728762528 Mean: 0.642312324367723897
    {1} Count: 17967.692701770462 Mean: 0.357687675632276214

```