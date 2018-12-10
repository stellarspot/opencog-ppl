# Belief Propagation on Bayesian Network

## Bayesian Network


Bayesian Network represents a set of variables and their conditional dependencies
via a directed acyclic graph (DAG).


## Grass is Wet Sample


Graph in form of node <- parents:

Sprinkler <- Rain
Grass <- Sprinkler, Rain

Rain:

| F   | T   |
| --- | --- |
| 0.2 | 0.8 |

Sprinkler:

| Rain | F    | T    |
| ---- | ---- | ---- |
| F    | 0.6  | 0.4  |
| T    | 0.99 | 0.01 |


Grass is wet:

|Sprinkler| Rain | F    | T    |
| ------- | ---- | ---- | ---- |
| F       | F    | 1.0  | 0.1  |
| F       | T    | 0.2  | 0.8  |
| T       | F    | 0.1  | 0.9  |
| T       | T    | 0.01 | 0.99 |


P(G, S, R) = P(G|S,R) P(S|R) P(R)

## Grass is Wet Sample Sample Factorization

P(G, S, R) = P1(G|S,R) P2(S|R) P3(R)

G, S, R <- P1

S, R    <- P2

R       <- P3

## OpenCog Representation

```scheme
(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "True")))

(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "False")))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "False"))
  (AssociativeLink (Concept "Sprinkler") (Concept "False"))
 )
)

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "False"))
  (AssociativeLink (Concept "Sprinkler") (Concept "True"))
 )
)
```
