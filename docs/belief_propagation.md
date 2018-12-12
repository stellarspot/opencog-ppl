# Belief Propagation algorithm implementation in OpenCog

Example: Sherlock Holmes and wet grass

## Bayesian network

HG - grass is wet on Holmes's lawn  
WG - grass is wet on Watson's lawn  
S - sprinkler was turned on  
R - there was a rain

![Bayesian Network](images/belief_propagation/holmes_grass_bayesian_network.png)

P(HG, WG, S, R) = P(HG|S,R) P(WG|R)  P(S) * P(R)

Was there a rain if Holmes's grass is wet?

P(R=true|HG=wet) = P(R=true, HG=wet) / P(HG=wet)
  = Sum[S, WG] P(HG=wet, WG, S, R=true) / Sum[WG, S, R] P(HG=wet, WG, S, R)


Was there a rain if Holmes's and Watson's grass is wet?

P(R=true|HG=wet, WG=wet) = P(R=true, HG=wet, WG=wet) / P(HG=wet, WG=wet)
  = Sum[S] P(HG=wet, WG=wet, S, R=true) / Sum[S, R] P(HG=wet, WG=wet, S, R)

## Factorization

Create a bipartite graph where one set of vertices are functions and another set are variables:

P(HG, WG, S, R) = P(HG|S,R) P(WG|R) P(S) * P(R) = P1(HG,S,R) P2(WG,R) P3(S) * P3(R)

![Bayesian Network Factorization](images/belief_propagation/holmes_grass_factorization.png)

## Factor Tree

The algorithm will be used for trees:

![Bayesian Network Factor Tree](images/belief_propagation/holmes_grass_factor_tree.png)

## Messages sending on Factor tree

Message from variable i to factor f:  
M(i->f) = Mul[g, g!=f] M (g->i)

Initial message from variable i to factor f for leaf variables:  
M(i->f) = [1, 1, ... , 1]

![Bayesian Network Factor Tree](images/belief_propagation/factor_tree_message_var_f.png)

Message from factor f to variable i:  
M(f->i) = Sum[j, j !=i] f(X) Mul(j, j!=i) M [j->f]

Initial message from factor f to variable i for leaf factors:  
M(i->f) = [f(V1), f(V2), ... , f(Vn)]

![Bayesian Network Factor Tree](images/belief_propagation/factor_tree_message_f_var.png)


## Algorithm Steps

Task solution steps:
1. Define probability values
1. Define evidences
1. Define marginal distributions to calculate
1. Create a factor tree
1. Run Belief Propagation algorithm

### Probability Values

Rain: true, false  
Sprinkler: switch-on, switch-off  
Grass: wet, dry

P(R)

|true |false |
|-----|------|
|  0.2|   0.8|

P(S)

|true |false |
|-----|------|
|  0.1|   0.9|


P(WG|R)

|    R|   wet|       dry|
|-----|------|----------|
|true |1     |         0|
|false|0.2   |       0.8|


P(HG|S, R)

|         S|    R|   wet|       dry|
|----------|-----|------|----------|
|switch-on |true |1     |         0|
|switch-on |false|0.9   |       0.1|
|switch-off|true |1     |         0|
|switch-off|false|0     |         1|

### OpenCog representation

```scheme
; Gras is wet or dry
(InheritanceLink (Concept "wet") (Concept "Grass"))
(InheritanceLink (Concept "dry") (Concept "Grass"))

(EvaluationLink
 (PredicateNode "type")
 (AssociativeLink (Concept "HolmesGrass") (Concept "Grass")))

; Probabilities
(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "true" (stv 0.2 1))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "true" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet" (stv 1.0 1)))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet" (stv 1.0 1)))))

; Evidences
(EvaluationLink
 (PredicateNode "evidence")
 (AssociativeLink (Concept "WatsonGrass") (Concept "wet" (stv 1.0 1))))

(EvaluationLink
 (PredicateNode "evidence")
 (AssociativeLink (Concept "HolmesGrass") (Concept "wet" (stv 1.0 1))))
```


### Posterior probabilities

Sample:

P(R=true|HG=wet, WG=wet) = P(R=true, HG=wet, WG=wet) / P(HG=wet, WG=wet) 
  = Sum[S] P(HG=wet, WG=wet, S, R=true) / Sum[S, R] P(HG=wet, WG=wet, S, R)

### Marginal probabilities

Two marginal probabilities should be calculated:
* Sum[S] P(HG=wet, WG=wet, S, R=true)  
  HG=wet, WG=wet, and R=true are evidences
* Sum[S, R] P(HG=wet, WG=wet, S, R)  
  HG=wet and WG=wet are evidences

### Creating Factor Graph

Factor graph needs to be created from probability predicates.
For each probability predicate there should be generated edge (Factor to Variable)
and factor argument list used to calculate factor for the given variables.


Probability predicates:
```scheme
; Probabilities
(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "true" (stv 0.2 1))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "true" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet" (stv 1.0 1)))))

```

Generated edges:
```scheme
(EvaluationLink
 (PredicateNode "graph-edge")
 (AssociativeLink (Concept "P4") (Concept "Rain" )))

(EvaluationLink
 (PredicateNode "graph-edge")
 (AssociativeLink (Concept "P2") (Concept "Rain" )))

(EvaluationLink
 (PredicateNode "graph-edge")
 (AssociativeLink (Concept "P2") (Concept "WatsonGrass" )))
```

Generated factor arguments list:
```scheme
(EvaluationLink
 (PredicateNode "factor-arguments-list")
 (AndLink
  (Concept "P4")
  (Concept "Rain")))

(EvaluationLink
 (PredicateNode "factor-arguments-list")
 (AndLink
  (Concept "P2")
  (Concept "Rain")
  (Concept "WatsonGrass")))
```

Where graph edge is of the form:
```text
EvaluationLink
  PredicateNode "graph-edge"
  AssociativeLink Factor Variable
```

And factor argument list is of the form:
```text
EvaluationLink
  PredicateNode "factor-arguments-list"
  AndLink
    Factor
    Variable1
    VariableN
```

* For each factor there should be generated unique index/postfix.
* Factors for the same "probability" predicate must have the same index/postfix

### Run Belief Propagation algorithm

Each variable Xi has a domain (V1, ..., Vn)

Note, if there is an evidence for some variable its domain is reduced only to one value.

Message from variable i to factor f:
```text
If there is no messages from variable i to f:
  Get a set of edges from factor g to i where g!=f
    If the set is empty, send initial message M(i->f) = [1, ..., 1]
      where the vector size is the size of the variable i domain
    If the set size is number of incoming factors minus 1
        (all connected factors except f have messages to i)
      send componentwise multiplication of the messages
    Else do nothing (not all messages are arrived)
```

Message from factor f to variable i:
```text
If there is no messages from variable i to f:
  Get set of edges from variable j to factor f where j!=i
    If the set is empty, send initial message M(f->i)=[f(Xi=v1), ..., f(Xi)=vn]
      where the message size is the size of the variable i domain
    If the set size is number of incoming variables minus 1
        (all connected variables except i have messages to f)
      calculate tensor from F from f
        F = (f(X1=v11, X2=v21), ..., f(X1=v1n, X2=v2n))
      multiply the tensor F to all incoming messages except variable i:
      M(f->i)=Sum[k] F * M[k->f] where k!=i
    Else do nothing (not all messages are arrived)
```

* Generate messages using URE/PLN
* Work until all factors and variables have incoming messages.

### Messages sample

Lets take a look at the simplified factor graph there are only Rain and Watson Grass is present:
![Watson Grass and Rain](images/belief_propagation/watson_grass_and_rain_factor_tree.png)

Initial message from variable Watson Grass to factor P2
```scheme
(EvaluationLink
 (PredicateNode "graph-message")
 (AndLink
  (Concept "WatsonGraph")
  (Concept "P2")
  (AndLink (Number "1") (Number "1"))))
```

Initial message from factor P4 to variable Rain
```scheme
(EvaluationLink
 (PredicateNode "graph-message")
 (AndLink
  (Concept "P4")
  (Concept "Rain")
  (AndLink (Number "P4(Rain=false)") (Number "P4(Rain=true)"))))
```

Message from variable Rain to factor P2
```scheme
(EvaluationLink
 (PredicateNode "graph-message")
 (AndLink
  (Concept "Rain")
  (Concept "P2")
  (AndLink (Number "1") (Number "1"))))
```

Message from factor P2 to variable Rain
```scheme
(EvaluationLink
 (PredicateNode "graph-message")
 (AndLink
  (Concept "P2")
  (Concept "Rain")
  (AndLink
   (Number "P2(Rain=false, WatsonGrass=dry) * 1 + P2(Rain=false, WatsonGrass=wet) * 1")
   (Number "P2(Rain=true, WatsonGrass=dry) * 1 + P2(Rain=true, WatsonGrass=wet) * 1"))))
```