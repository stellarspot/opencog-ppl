# Belief Propagation algorithm implementation in OpenCog

## Reference Implementation

The reference implementation is written in Python:
* [Belief Propagation URE Rules](../opencog/samples/belief-propagation/python/belief_propagation_ure.py)
* [Belief Propagation Rain Wet Grass Sample](../opencog/samples/belief-propagation/python/sample-rain-wet-grass.py)


## Known problems

[Python file is not loaded in SCM](https://github.com/opencog/atomspace/issues/1888)
[Using GlobNode in Backward Chainer](https://github.com/opencog/atomspace/issues/2009)
[ForAllLink does not returns values](https://github.com/opencog/atomspace/issues/2018)

## Simple Grass and Rain sample

Lets take a look at the simplified factor graph there are only Rain and WastsonGrass are present:

Rain: true, false  
Wet Grass: wet, dry

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

Factorization:  
P(WG, R) = P1(WG, R) P2(R)

![Watson Grass and Rain](images/belief_propagation/watson_grass_and_rain_factor_tree.png)

The task is to calculate a probability of rain given grass is wet:

P(R=true|WG=wet) = P(R=true, WG=wet) / P(WG=wet)


## Task Definition

```scheme
(define R (ConceptNode "Rain"))
(define W (ConceptNode "WetGrass"))
(define WR (Implication R W))


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
```

## Main Steps

The task is split on steps:
* Factor graph generation
* Messages sending
* Calculation of final probability

## Factor Graph generation

The first step is generation a factor graph using the initial task representation.

Rules:
* (Concept A) with DV ->
  * Variable
    * Predicate('Variable', 'Variable-A')
  * Factor
    * Predicate('Factor', 'Factor-A')
  * Edge
    * Predicate('Edge', 'Factor-A', 'Variable-A')
* (Implication (Concept B) (Concept A)) with DV
  * Variables
    * Predicate('Variable', 'Variable-A')
    * Predicate('Variable', 'Variable-B')
  * Factor
    * Predicate('Factor', 'Factor-A-B')
  * Edge
    * Predicate('Edge', 'Factor-A-B', 'Variable-A')
    * Predicate('Edge', 'Factor-A-B', 'Variable-B')
* (Implication (Product (Concept B)(Concept C)) (Concept A)) with DV
  * Variables
    * Predicate('Variable', 'Variable-A')
    * Predicate('Variable', 'Variable-B')
    * Predicate('Variable', 'Variable-C')
  * Factor
    * Predicate('Factor', 'Factor-A-B-C')
  * Edge
    * Predicate('Edge', 'Factor-A-B-C', 'Variable-A')
    * Predicate('Edge', 'Factor-A-B-C', 'Variable-B')
    * Predicate('Edge', 'Factor-A-B-C', 'Variable-C')

Additional rules:
  * Variable  shape: size of the appropriate dimension of DV according to the order of variables in Implication link
  * Factor tensor: DV from Implication link
  * Factor shape: dimensions of DV value

## Message Sending

Messages are vectors which are connected as values to Edges.
There are two keys:
  * 'message-variable-factor-key' for messages from variable to factor
  * 'message-factor-variable-key' for messages from factor to variable


**Message from Variable V to Factor F**

Conditions:
* There is no message from V to F
* For each edge between factor G to variable V and G != F there is a message from G to V

Message value:
* Componentwise multiplication of the messages from FF to V

M(V->F) = Mul[G, G!=F] M (G->V)

Initial message leaf variables:  
M(V->F) = [1, 1, ... , 1]

where the size of the message is shape of the variable

![Bayesian Network Factor Tree](images/belief_propagation/factor_tree_message_var_f.png)


**Message from Factor F to Variable V**

Conditions:
* There is no message from F to V
* For each edge between factor F to variable VV and VV != V there is a message from VV to F

Message value:
* Multiply the tensor F to all incoming messages except variable V

M(F->V) = Mul[U, U !=V] tensor(F) M[U->F]

Initial message for leaf factors:  
M(F->V) = [f(V1), f(V2), ... , f(Vn)]

![Bayesian Network Factor Tree](images/belief_propagation/factor_tree_message_f_var.png)

## Simple Grass and Rain Factor Graph

Variable:
```scheme
(define R (ConceptNode "Rain"))
(cog-set-value! R key (cog-new-dv zo '(80000 20000)))

```
to
```scheme
(SetLink
   (ListLink
      (EvaluationLink
         (PredicateNode "factor-node")
         (ConceptNode "Factor-Rain")
      )
      (EvaluationLink
         (PredicateNode "variable-node")
         (ConceptNode "Variable-Rain")
      )
      (EvaluationLink
         (PredicateNode "graph-edge")
         (ListLink
            (ConceptNode "Factor-Rain")
            (ConceptNode "Variable-Rain")
         )
      )
   )
)

```

Implication:
```scheme
(define WR (Implication R W))

(define dvWR0 (cog-new-dv zo '(75000 25000)))
(define dvWR1 (cog-new-dv zo '(10000 90000)))

(define dvWR (cog-new-cdv zo (list dvWR0 dvWR1)))
(cog-set-value! WR key dvWR)
```
to
```scheme
(SetLink
   (ListLink
      (EvaluationLink
         (PredicateNode "factor-node")
         (ConceptNode "Factor-Rain-WetGrass")
      )
      (EvaluationLink
         (PredicateNode "variable-node")
         (ConceptNode "Variable-Rain")
      )
      (EvaluationLink
         (PredicateNode "variable-node")
         (ConceptNode "Variable-WetGrass")
      )
      (EvaluationLink
         (PredicateNode "graph-edge")
         (ListLink
            (ConceptNode "Factor-Rain-WetGrass")
            (ConceptNode "Variable-Rain")
         )
      )
      (EvaluationLink
         (PredicateNode "graph-edge")
         (ListLink
            (ConceptNode "Factor-Rain-WetGrass")
            (ConceptNode "Variable-WetGrass")
         )
      )
   )
)
```
## Methods

Factor Graph Initialization:
* init_factor_graph()

Messages sending:
* send_messages()
