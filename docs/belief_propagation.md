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
