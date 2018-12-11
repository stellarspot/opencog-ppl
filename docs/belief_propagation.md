# Belief Propagation algorithm implementation in OpenCog

Example: Sherlock Holmes and wet grass

## Bayesian network

HG - grass is wet on Holmes's lawn  
WG - grass is wet on Watson's lawn  
S - sprinkler was turned on  
R - there was a rain

![Bayesian Network](images/belief_propagation/holmes_grass_bayesian_network.png)

P(HG, WG, S, R) = P(HG|S,R) P(WG|R)  P(S) * P(R)

P(HG=T|WG=T) = P(HG=T, WG=T) / P(WG=T) = Sum[S,R] P(HG=T, WG=T, S, R) / Sum[HG, S,R] P(HG, WG=T, S, R)

## Factorization

Create a bipartite graph where one set of vertices are functions and another set are variables:

P(HG, WG, S, R) = P(HG|S,R) P(WG|R) P(S) * P(R) = P1(HG,S,R) P2(WG,R) P3(S) * P3(R)

![Bayesian Network Factorization](images/belief_propagation/holmes_grass_factorization.png)

## Factor Tree

The algorithm will be used for trees:

![Bayesian Network Factor Tree](images/belief_propagation/holmes_grass_factor_tree.png)

## Messages:

Message from node i to factor f:  
M(i->f) = Mul[g, g!=f] M (g->i)

![Bayesian Network Factor Tree](images/belief_propagation/factor_tree_message_var_f.png)


Message from factor f to node i:  
M(f->i) = Sum[j, j !=i] f(X) Mul(j, j!=i) M [j->f]

![Bayesian Network Factor Tree](images/belief_propagation/factor_tree_message_f_var.png)

Initial Values for leaves:

From node i to factor f:
M(i->f) = [1, 1]

From from factor f to node i:
M(i->f) = [f(False), f(True)]

## Algorithm Steps

1. Define Probability values
1. Define marginal distribution to calculate
1. Restrict probabilities to known events
1. Create a factor tree
1. Run Belief Propagation algorithm

### Probability Values

Rain: true, false  
Sprinkler: switch-on, switch-off  
Grass: is-wet, is-not-wet


P(R)

|true |false |
|-----|------|
|  0.2|   0.8|

P(S)

|true |false |
|-----|------|
|  0.1|   0.9|


P(WG|R)

|R\WG |is-wet|is-not-wet|
|-----|------|----------|
|true |1     |         0|
|false|0.2   |       0.8|


P(HG|S, R)

|         S|    R|is-wet|is-not-wet|
|----------|-----|------|----------|
|switch-on |true |1     |         0|
|switch-on |false|0.9   |       0.1|
|switch-off|true |1     |         0|
|switch-off|false|0     |         1|


Sample:  
P(HG=T|WG=T) = P(HG=T, WG=T) / P(WG=T) = Sum[S,R] P(HG=T, WG=T, S, R) / Sum[HG, S,R] P(HG, WG=T, S, R)

Two marginal probabilities should be calculated:
* Sum[S,R] P(HG=T, WG=T, S, R)  
  Both WG and HG values must be restricted 
* Sum[HG, S,R] P(HG, WG=T, S, R)  
  WG value must be restricted
  


